# Tenging við Hlaðvarp.com

Setjið hnapp á skjáinn þar sem notandi er að setja inn eða breyta þætti. Hnappurinn opnar upptökutólið með upplýsingum um þáttinn í slóðinni.

## Einfaldur hnappur

```html
<a
  class="btn btn-main"
  href="/studio-recorder/?source=hladvarp&episodeId=123&episodeTitle=N%C3%BDr%20%C3%BE%C3%A1ttur&showTitle=Kaffispjall&returnUrl=%2Fcp-admin%2Fstudio"
>
  Nota upptökutól
</a>
```

Í production væri `/studio-recorder/` slóðin þar sem þetta tól er hýst innan `hladvarp.com`.

## JavaScript dæmi

```js
function openRecorderForEpisode(episode) {
  const url = new URL("/studio-recorder/", window.location.origin);
  url.searchParams.set("source", "hladvarp");
  url.searchParams.set("episodeId", episode.id);
  url.searchParams.set("episodeTitle", episode.title);
  url.searchParams.set("showTitle", episode.showTitle);
  url.searchParams.set("returnUrl", window.location.href);
  url.searchParams.set("uploadToken", episode.uploadToken);

  window.open(url, "hladvarpRecorder", "width=1280,height=840");
}

window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin) {
    return;
  }

  if (event.data?.type === "hladvarp-recording-ready") {
    console.log("Upptaka tilbúin fyrir þátt", event.data.episodeId, event.data.recording);
  }
});
```

## Gögn sem upptökutólið sendir

Upptakan er send með `POST /api/recordings`. Þessi header-gildi fylgja:

- `X-Recording-Name`
- `X-Episode-Id`
- `X-Episode-Title`
- `X-Show-Title`
- `X-Hladvarp-Tool`

Local `server.py` vistar hljóðskrána í `recordings/` og býr líka til `.json` hliðarskrá með metadata.

## Production kröfur

Upptökutólið þarf að keyra á HTTPS. `localhost` virkar í þróun, en production þarf örugga slóð.

Mikilvægt: núverandi public header á `hladvarp.com` er með `Permissions-Policy: microphone=()`. Það lokar á hljóðnemann ef upptökutólið er hýst undir sömu global stillingu. Fyrir upptökuslóðina þarf header svipaðan þessu:

```http
Permissions-Policy: microphone=(self), camera=(), geolocation=()
```

Mælt er með popup eða sér síðu, ekki iframe, því public vefurinn er líka með `X-Frame-Options: DENY`.

## Leyfi og eigendaprófun

Í production á `/api/recordings` að staðfesta að innskráði notandinn megi breyta viðkomandi `episodeId`. Local serverinn styður upload-token hook:

- setja `HLADVARP_STUDIO_TOKEN` á servernum
- senda sama token sem `uploadToken` í slóð eða `Authorization: Bearer ...`

Þetta er þróunarhook. Raunverulegt Hlaðvarp.com ætti að tengja þetta við núverandi session/innskráningu og ownership-prófun.

## MP3 umbreyting

Local serverinn getur reynt MP3 umbreytingu ef:

- `ffmpeg` er uppsett
- `HLADVARP_ENABLE_MP3=1`

Annars vistast upprunalega vafraupptakan, oftast `.webm` með Opus hljóði.
