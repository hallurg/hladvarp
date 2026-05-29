# Deployment

## Keyra á server

```bash
export HOST=127.0.0.1
export PORT=8000
export HLADVARP_STUDIO_TOKEN="setja-sterkan-token-her"
export HLADVARP_ENABLE_MP3=1
python server.py
```

Setjið reverse proxy fyrir `/studio-recorder/`, `/api/recordings` og `/api/health` yfir á `127.0.0.1:8000`.

## Docker

```bash
docker build -t hladvarp-studio .
docker run --rm -p 8000:8000 \
  -e HLADVARP_STUDIO_TOKEN="setja-sterkan-token-her" \
  -e HLADVARP_ENABLE_MP3=1 \
  -v hladvarp-recordings:/app/recordings \
  hladvarp-studio
```

## Hljóðnemi í production

Upptökuslóðin þarf HTTPS og þennan header eða sambærilegt:

```http
Permissions-Policy: microphone=(self), camera=(), geolocation=()
```

Public vefurinn má áfram hafa strangari stillingar fyrir aðrar slóðir, en `/studio-recorder/` má ekki fá `microphone=()`.

## Staðfesting eftir deploy

```bash
curl https://hladvarp.com/api/health
```

Síðan opnið:

```text
https://hladvarp.com/studio-recorder/?source=hladvarp&episodeId=test&episodeTitle=Prufa&showTitle=Hlaðvarp
```
