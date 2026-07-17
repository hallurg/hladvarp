# Kaupfjelag Nærsveitamanna - Stjórnunarkerfi

Heildarstjórnunarkerfi fyrir starfsmenn, verkefni, viðskiptavini og reikninga.

## 🎨 Útlitshönnun

Kerfið er hannað samkvæmt Kaupfjelag Nærsveitamanna lógói:
- **Hnappar**: Appelsínugulir (#D97525) með svörtu letri
- **Bakgrunnur**: Blár (#2E3192) með hvítu letri  
- **Innsláttarreitir og mælaborð**: Hvítir með svörtum texta
- **Áherslur**: Appelsínugul borðar og áherslupunktar

## Eiginleikar

### Starfsmannastjórnun
- Ítarleg starfsmannaskráning með persónuupplýsingum
- QR kóða aðgangsstýring
- Sjálfvirk mætingaskráning
- Frídagaumsýsla
- Veikindaskráning

### Verkefnastjórnun
- Verkbeiðnakerfi
- Úthlutun verkefna á starfsmenn
- Eftirfylgni og deadline áminningar
- Skráarmöppur fyrir skjámyndir og skjöl

### Viðskiptamannabókhald
- Viðskiptavinaskrá með ítarlegum upplýsingum
- Skuldastaða og greiðsluferill
- Staða verkefna

### Reikningakerfi
- Sjálfvirkir reikningar
- Kostnaðarskráning (vinnukostnaður + efniskostnaður)
- Fastir gjaldliðir
- Útkalla vs vinnustaður skráning
- **PDF útskrift reikninga**

### Bókhaldskerfi
- **Bókhaldslyklar (Chart of Accounts)** - eins og í DK
- **Debet/Kredit bókhald**
- Bókhaldsfærslur (tekjur og gjöld)
- Fjárstreymisyfirlit
- Fjárhagsleg samantekt
- **Ársreikningar í PDF**
- Tengingar við viðskiptavini og starfsmenn

### 📄 PDF Skýrslur
Hægt er að búa til PDF skýrslur úr öllum valmyndum:
- Starfsmannaskrá
- Mætingaskrá
- Viðskiptavinaskrá
- Verkefnalisti
- Reikningalisti
- Bókhaldsfærslur
- Ársreikningar

### Aðgangsstig
- **Super Admin**: Heildarumsjón yfir öllum kerfum
- **Sub Admin**: Yfirmaður vinnustaðar
- **Starfsmaður**: Venjulegur notandi

### Super-admin viðmót (aðgangsstýring + opna kerfi)
- Super-admin á að vinna í sérstöku viðmóti þar sem aðeins er stýrt hverjir hafa aðgang að kerfinu.
- Sérsniðið admin mælaborð er aðgengilegt á `admin/super-admin/`.
- Fyrir hvern kerfiskaupanda er hægt að smella á **"Opna kerfi"** og opna kerfið í sér glugga.
- Það flæði notar endpoint: `GET /api/bokhald/kerfiskaupendur/{id}/opna-kerfi/`
- Fyrir beint redirect í nýjan glugga: `GET /api/bokhald/kerfiskaupendur/{id}/opna-kerfi/?redirect=1`
- Sjálfgefið notar endpoint **one-time launch code** (ekki access token í URL):
	- Opna: `GET /api/bokhald/kerfiskaupendur/{id}/opna-kerfi/?redirect=1&delivery=code`
	- Nýr gluggi skiptir kóða í tokens með: `POST /api/bokhald/kerfiskaupendur/consume-launch-code/` með `{ "launch_code": "..." }`
- Fyrir afturvirkt samhæfi er enn hægt að nota `delivery=token`.
- Hægt er að stilla áfangaslóð fyrir glugga með `SUPERADMIN_LAUNCH_URL` (default: `/admin/`).
- Hægt er að takmarka leyfð host fyrir `redirect_url` með `SUPERADMIN_ALLOWED_REDIRECT_HOSTS`.
- Gildistími launch code er stillanlegur með `SUPERADMIN_LAUNCH_CODE_TTL_SECONDS` (default: `90`).

### Gagnareglur fyrir kerfiskaupendur
- `Kennitala` er vistuð á forminu `XXXXXX-XXXX` (10 tölustafir með bandstriki eftir 6 stafi).
- `Símanúmer` fylgir lengdarreglum út frá `Land`.
- `Landsnúmer` er sett sjálfvirkt út frá `Land`.
- Heimilisfang er skipt í reitina: `Heimilisfang`, `Póstnúmer`, `Sveitarfélag`, `Land`.
- Fyrir `Land = Island` er `Sveitarfélag` fyllt sjálfvirkt út þegar póstnúmer finnst í lookup töflu.
- Í admin formi eru sömu reglur keyrðar "live": kennitala formatting, póstnúmer/sveitarfélag lookup, landsnúmer + símalengd eftir landi.

### Splashscreen við opnun
- Vörumerktur splashscreen birtist í `3 sek` þegar admin kerfið opnast.
- Splashscreen birtist einu sinni í hverri browser session (per tab) til að trufla ekki flæði á hverri síðu.

## Uppsetning

```bash
# Setja upp virtual environment
python -m venv venv
venv\Scripts\activate

# Setja upp dependencies
pip install -r requirements.txt

# Keyra migrations
python manage.py makemigrations
python manage.py migrate

# Búa til super admin
python manage.py createsuperuser

# Keyra server
python manage.py runserver
```

### Keyra test local (án PostgreSQL)

Þar sem appin eru ekki með full migration sett, er mælt með að keyra test með SQLite + slökkt á migrations:

```powershell
$env:DB_ENGINE='django.db.backends.sqlite3'
$env:DB_NAME=':memory:'
$env:DISABLE_MIGRATIONS='True'
C:/Python313/python.exe manage.py test -v 2
```

## Docker uppsetning á VPS (Ubuntu 24.04)

### 1) Undirbúa `.env`

Afritaðu `.env.example` yfir í `.env` og uppfærðu lykla:

```bash
cp .env.example .env
```

Mikilvægt:
- `SECRET_KEY` þarf að vera sterkur, leynilegur lykill
- `DB_PASSWORD` þarf að vera sterkt lykilorð
- `ALLOWED_HOSTS` þarf að innihalda IP/domain
- `CORS_ALLOWED_ORIGINS` þarf að innihalda desktop/web origin sem nota API

### 2) Keyra Docker stack

```bash
docker compose build
docker compose up -d
```

### 3) SSL/TLS

Let’s Encrypt virkar best með **domain** (ekki beint með IP).

Ef domain er tilbúið (t.d. `api.example.is`):

```bash
docker compose run --rm certbot certonly \
	--webroot -w /var/www/certbot \
	-d api.example.is \
	--email you@example.is --agree-tos --no-eff-email

docker compose restart nginx
```

Opnuð port á VPS:
- `22/tcp` (SSH)
- `80/tcp` (HTTP/acme challenge)
- `443/tcp` (HTTPS)

## Desktop keyrsla (EXE)

- **Sub-admin**: keyrir local sem `.exe`, tengist remote API yfir HTTPS.
- **Super-admin**: keyrir local sem `.exe`, sér eingöngu kerfiskaupendur og getur opnað hvert kerfi með super-admin session.

Mælt er með að nota Electron fyrir bæði desktop forritin og JWT access tokens með stuttan líftíma + refresh token.

## Tæknistafl

- **Backend**: Django 5.0 + Django REST Framework
- **Gagnagrunnur**: PostgreSQL
- **Authentication**: JWT tokens
- **QR kóðar**: qrcode library
- **Skýrslur**: ReportLab
- **Task Queue**: Celery + Redis
