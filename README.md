# Hlaðvarp Studio

Vefapp til að búa til tímasett podcast-handrit, keyra niðurteljara og taka upp hljóð beint í vafra.

## Keyrsla

```powershell
python server.py
```

Farðu síðan á `http://localhost:8000`.

Upptaka í vafra þarf öruggt samhengi. `localhost` telst öruggt í þróun, en production þarf HTTPS.

Tólið má líka keyra undir `/studio-recorder/` í production. Serverinn þjónar sama appi á `/` og `/studio-recorder/`.

## Hvað er komið

- Hljóðupptaka beint í vafra með `MediaRecorder`.
- Hlustun, bein sending inn í app/server og niðurhal eftir upptöku.
- Heildarniðurteljari og niðurteljari fyrir hvern kafla.
- Áminning 5 mínútum áður en kafli lýkur.
- Auglýsingaráminning milli kafla þegar hakað er við hana.
- Einföld málefnagreining úr handriti/punktum.
- URL-tenging frá Hlaðvarp.com með `episodeId`, `episodeTitle`, `showTitle`, `returnUrl` og valfrjálsu `uploadToken`.
- `/api/health` readiness endpoint.
- Optional upload-token vörn með `HLADVARP_STUDIO_TOKEN`.
- Optional MP3 hook með `HLADVARP_ENABLE_MP3=1` ef `ffmpeg` er uppsett.

## Dæmi um tengingu frá Hlaðvarp.com

```text
/studio-recorder/?source=hladvarp&episodeId=123&episodeTitle=N%C3%BDr%20%C3%BE%C3%A1ttur&showTitle=Kaffispjall&returnUrl=%2Fcp-admin%2Fstudio
```

Sjá `HLADVARP_INTEGRATION.md` fyrir hnapp og production stillingar.

Health/readiness upplýsingar eru á `http://localhost:8000/api/health`.

Sjá `DEPLOYMENT.md` fyrir Docker, Caddy/reverse proxy og production keyrslu.

## Production atriði

Fyrir upptökuslóðina þarf hljóðnemi að vera leyfður:

```http
Permissions-Policy: microphone=(self), camera=(), geolocation=()
```

Public vefurinn má vera með strangari stillingar, en upptökutólið sjálft þarf að keyra á slóð þar sem browserinn fær microphone access.
