# Production Readiness Yfirferð

## Staðfest local

- Vefupptaka er til staðar með `MediaRecorder`.
- Tímastýring, kaflar, 5 mínútna áminningar og auglýsingaráminningar eru til staðar.
- Beint upload á `/api/recordings` er til staðar.
- Upptaka vistast í `recordings/`.
- Metadata fyrir `episodeId`, `episodeTitle` og `showTitle` vistast í `.json` hliðarskrá.
- Health-endapunktur er til staðar á `/api/health`.
- Upload-token hook er til staðar með `HLADVARP_STUDIO_TOKEN`.
- Optional MP3 hook er til staðar með `HLADVARP_ENABLE_MP3=1` ef `ffmpeg` er uppsett.

## Staðfest á public hladvarp.com utan frá

- Forsíða svarar `200`.
- `/cp-admin/studio` redirectar á `/cp-auth/login`.
- `/studio-recorder/` er ekki enn deployað á public vefnum.
- Public headers innihalda `Permissions-Policy: microphone=()` og `X-Frame-Options: DENY`.

## Það sem þarf í production

- Deploya tólið á t.d. `/studio-recorder/`.
- Setja hnappinn úr `HLADVARP_INTEGRATION.md` á „setja inn þátt“ eða „breyta þætti“ skjá.
- Breyta header fyrir upptökuslóðina í `Permissions-Policy: microphone=(self), camera=(), geolocation=()`.
- Láta `/api/recordings` nota núverandi Hlaðvarp.com innskráningu og staðfesta ownership á `episodeId`.
- Setja varanlega skráageymslu fyrir hljóðskrár.
- Setja upp `ffmpeg` og `HLADVARP_ENABLE_MP3=1` ef MP3 á að verða sjálfgefið output.
