from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import json
import mimetypes
import os
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
RECORDINGS_DIR = ROOT / "recordings"
UPLOAD_TOKEN = os.environ.get("HLADVARP_STUDIO_TOKEN", "").strip()
ENABLE_MP3 = os.environ.get("HLADVARP_ENABLE_MP3", "").strip() == "1"
FFMPEG = shutil.which("ffmpeg")


def safe_file_name(raw_name: str, content_type: str) -> str:
    decoded = unquote(raw_name or "").strip()
    decoded = Path(decoded).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", decoded).strip(".-")

    if cleaned:
        return cleaned

    extension = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".webm"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"podcast-upptaka-{stamp}{extension}"


def json_response(handler, status: int, data: dict):
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def mp3_status(source: Path) -> dict:
    if not ENABLE_MP3:
        return {"enabled": False, "status": "disabled"}

    if not FFMPEG:
        return {"enabled": True, "status": "missing-ffmpeg"}

    target = source.with_suffix(".mp3")
    command = [
        FFMPEG,
        "-y",
        "-i",
        str(source),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-b:a",
        "192k",
        str(target),
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return {
            "enabled": True,
            "status": "failed",
            "error": result.stderr[-800:],
        }

    return {
        "enabled": True,
        "status": "created",
        "fileName": target.name,
        "relativePath": f"recordings/{target.name}",
        "bytes": target.stat().st_size,
    }


class PodcastHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if urlparse(self.path).path != "/api/health":
            super().do_GET()
            return

        json_response(self, 200, {
            "ok": True,
            "storage": {
                "recordingsDir": str(RECORDINGS_DIR),
                "exists": RECORDINGS_DIR.exists(),
            },
            "uploadAuth": {
                "tokenRequired": bool(UPLOAD_TOKEN),
                "mode": "bearer-token" if UPLOAD_TOKEN else "local-open",
            },
            "mp3": {
                "enabled": ENABLE_MP3,
                "ffmpegAvailable": bool(FFMPEG),
            },
            "browserRecording": {
                "requiresSecureContext": True,
                "localhostAllowed": True,
                "productionHeader": "Permissions-Policy: microphone=(self), camera=(), geolocation=()",
            },
        })

    def do_POST(self):
        if urlparse(self.path).path != "/api/recordings":
            self.send_error(404, "Unknown endpoint")
            return

        if UPLOAD_TOKEN and not self.has_valid_upload_token():
            self.send_error(401, "Invalid upload token")
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            self.send_error(400, "Missing recording body")
            return

        content_type = self.headers.get("Content-Type", "application/octet-stream")
        raw_name = self.headers.get("X-Recording-Name", "")
        file_name = safe_file_name(raw_name, content_type)
        RECORDINGS_DIR.mkdir(exist_ok=True)

        target = RECORDINGS_DIR / file_name
        if target.exists():
            stem = target.stem
            suffix = target.suffix
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            target = RECORDINGS_DIR / f"{stem}-{stamp}{suffix}"

        with target.open("wb") as recording_file:
            remaining = length
            while remaining:
                chunk = self.rfile.read(min(1024 * 1024, remaining))
                if not chunk:
                    break
                recording_file.write(chunk)
                remaining -= len(chunk)

        mp3 = mp3_status(target)
        metadata = {
            "receivedAt": datetime.now(timezone.utc).isoformat(),
            "episodeId": unquote(self.headers.get("X-Episode-Id", "")).strip(),
            "episodeTitle": unquote(self.headers.get("X-Episode-Title", "")).strip(),
            "showTitle": unquote(self.headers.get("X-Show-Title", "")).strip(),
            "tool": self.headers.get("X-Hladvarp-Tool", "").strip(),
            "contentType": content_type,
            "fileName": target.name,
            "relativePath": f"recordings/{target.name}",
            "bytes": target.stat().st_size,
            "mp3": mp3,
        }
        metadata_path = target.with_name(f"{target.name}.json")
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        response = {
            "ok": True,
            "fileName": target.name,
            "relativePath": f"recordings/{target.name}",
            "bytes": target.stat().st_size,
            "metadataPath": f"recordings/{metadata_path.name}",
            "episodeId": metadata["episodeId"],
            "mp3": mp3,
        }
        json_response(self, 201, response)

    def has_valid_upload_token(self) -> bool:
        auth = self.headers.get("Authorization", "")
        bearer = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else ""
        header_token = self.headers.get("X-Upload-Token", "").strip()
        return UPLOAD_TOKEN in {bearer, header_token}


def run():
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, PodcastHandler)
    print(f"Hlaðvarp Studio keyrir á http://{address[0]}:{address[1]}")
    print(f"Upptökur vistast í {RECORDINGS_DIR}")
    print(f"Upload token required: {bool(UPLOAD_TOKEN)}")
    print(f"MP3 conversion enabled: {ENABLE_MP3} (ffmpeg found: {bool(FFMPEG)})")
    server.serve_forever()


if __name__ == "__main__":
    run()
