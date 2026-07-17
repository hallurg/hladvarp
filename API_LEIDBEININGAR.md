# API Leiðbeiningar - Kaupfjelag Nærsveitamanna

## Auðkenning

Kerfið notar JWT (JSON Web Tokens) fyrir auðkenningu.

### Fá aðgangstoken

```bash
POST /api/token/
Content-Type: application/json

{
    "notandanafn": "admin",
    "password": "yourpassword"
}
```

**Svar:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1...",
    "access": "eyJ0eXAiOiJKV1..."
}
```

### Nota token í beiðnum

Bæta við í header:
```
Authorization: Bearer eyJ0eXAiOiJKV1...
```

## Notendategundir og réttindi

### SUPER_ADMIN
- Fullur aðgangur að öllu
- Sér alla kerfiskaupendur
- Getur búið til sub-admins

### SUB_ADMIN (Yfirmaður)
- Stjórnar sínum vinnustað
- Getur búið til og stjórnað starfsmönnum
- Samþykkir verkbeiðnir og frídaga
- Sér fjárhag og bókhald

### STARFSMADUR
- Sér sín verkefni
- Getur stimplað sig inn/út
- Getur óskað eftir frídögum
- Getur skráð vinnukostnað

## API Endpoints

### 1. Starfsfólk

#### Stofna nýjan starfsmann (SUB_ADMIN+)
```bash
POST /api/starfsfolk/starfsmenn/
Authorization: Bearer {token}
Content-Type: application/json

{
    "notandanafn": "jonsson",
    "email": "jonsson@example.is",
    "fullt_nafn": "Jón Jónsson",
    "lykilord": "password123",
    "kennitala": "0101013456",
    "heimilisfang": "Testgata 5, Reykjavík",
    "simanumer": "5551234",
    "active_directory_notandi": "jonsson@domain.com",
    "aeskilegur_moettartimi": "08:00:00",
    "aeskilegur_brottfararstimi": "17:00:00",
    "serhaefi_ids": [1, 2]
}
```

#### Fá alla starfsmenn
```bash
GET /api/starfsfolk/starfsmenn/
Authorization: Bearer {token}
```

#### Stimplast inn
```bash
POST /api/starfsfolk/maetingar/stimplast_inn/
Authorization: Bearer {token}
```

#### Stimplast út
```bash
POST /api/starfsfolk/maetingar/stimplast_ut/
Authorization: Bearer {token}
```

#### Mætingaryfirlit dagsins
```bash
GET /api/starfsfolk/maetingar/maetiyfirlit_dagsins/
Authorization: Bearer {token}
```

**Svar:**
```json
{
    "dagsetning": "2026-03-05",
    "tolur": {
        "maettir": 15,
        "fjarverandi": 2,
        "veikir": 1,
        "fri": 3,
        "utkoll": 4
    },
    "maetingar": [...]
}
```

#### Óska eftir frídegi
```bash
POST /api/starfsfolk/fridagar/
Authorization: Bearer {token}
Content-Type: application/json

{
    "starfsmadur": 1,
    "fra_dagsetning": "2026-04-01",
    "til_dagsetning": "2026-04-05",
    "fridags_tegund": "ORLOF",
    "lysing": "Páskaorlof"
}
```

#### Samþykkja frídagabeiðni (SUB_ADMIN+)
```bash
POST /api/starfsfolk/fridagar/{id}/samthykkja/
Authorization: Bearer {token}
```

### 2. Viðskiptavinir

#### Stofna nýjan viðskiptavin
```bash
POST /api/vidskiptavinir/
Authorization: Bearer {token}
Content-Type: application/json

{
    "nafn": "Test Ehf",
    "kennitala": "5501012340",
    "heimilisfang": "Fyrirtækjagata 10, Reykjavík",
    "simanumer": "5555678",
    "netfang": "test@example.is",
    "vsk_numer": "123456"
}
```

#### Fá fjárhagsupplýsingar viðskiptavinar
```bash
GET /api/vidskiptavinir/{id}/fjarhagur/
Authorization: Bearer {token}
```

**Svar:**
```json
{
    "vidskiptavinur": {...},
    "fjoldi_reikninga": 10,
    "heildar_reikningar": 500000.00,
    "heildar_greidslur": 300000.00,
    "skuldastada": 200000.00,
    "utistandandi_reikningar": 3
}
```

### 3. Verkefni

#### Stofna verkbeiðni
```bash
POST /api/verkefni/verkbeidnir/
Authorization: Bearer {token}
Content-Type: application/json

{
    "vidskiptavinur": 1,
    "titill": "Lagfæra rafmagn",
    "lysing": "Rafmagnsleysi í kjallara",
    "forgangur": "BRADALAST"
}
```

#### Samþykkja verkbeiðni (SUB_ADMIN+)
```bash
POST /api/verkefni/verkbeidnir/{id}/samthykkja/
Authorization: Bearer {token}
```

#### Úthluta verkefni
```bash
POST /api/verkefni/
Authorization: Bearer {token}
Content-Type: application/json

{
    "verkbeidni": 1,
    "starfsmadur": 2,
    "titill": "Rafmagnsviðgerð - Testgata 5",
    "lysing": "Athuga rafmagnslögn í kjallara",
    "vinnustadur": "UTKALL",
    "deadline": "2026-03-10T17:00:00Z"
}
```

#### Byrja á verkefni
```bash
POST /api/verkefni/{id}/byrja/
Authorization: Bearer {token}
```

#### Ljúka verkefni
```bash
POST /api/verkefni/{id}/ljuka/
Authorization: Bearer {token}
```

#### Hlaða upp skrá í verkefni
```bash
POST /api/verkefni/skrar/
Authorization: Bearer {token}
Content-Type: multipart/form-data

verkefni: 1
skra: [file]
tegund: SKJAMYND
lysing: Ljósmynd af viðgerð
```

#### Fá mín verkefni
```bash
GET /api/verkefni/min_verkefni/
Authorization: Bearer {token}
```

### 4. Reikningar

#### Stofna reikning
```bash
POST /api/reikningar/
Authorization: Bearer {token}
Content-Type: application/json

{
    "vidskiptavinur": 1,
    "verkefni": 3,
    "reikningsdagsetning": "2026-03-05",
    "gjalddagi": "2026-04-05",
    "eindagi": "2026-04-20",
    "heildarfjarhaed": 50000.00,
    "vsk_fjarhaed": 12000.00
}
```

#### Bæta línu við reikning
```bash
POST /api/reikningar/lidir/
Authorization: Bearer {token}
Content-Type: application/json

{
    "reikningur": 1,
    "lysing": "Vinnukostnaður 3 klst",
    "magn": 3,
    "einingarverð": 10000.00,
    "tegund": "VINNUKOSTNADUR"
}
```

#### Senda reikning
```bash
POST /api/reikningar/{id}/senda/
Authorization: Bearer {token}
```

#### Skrá greiðslu
```bash
POST /api/reikningar/greidslur/
Authorization: Bearer {token}
Content-Type: application/json

{
    "reikningur": 1,
    "fjarhaed": 50000.00,
    "greidsludagsetning": "2026-03-06",
    "greidslu_adferd": "MILLIFAERSLA"
}
```

#### Fá útistandandi reikninga
```bash
GET /api/reikningar/utistandandi/
Authorization: Bearer {token}
```

### 5. Bókhald

#### Skrá bókhaldsfærslu
```bash
POST /api/bokhald/faerslur/
Authorization: Bearer {token}
Content-Type: application/json

{
    "dagsetning": "2026-03-05",
    "lysing": "Kaup á verkfærum",
    "fjarhaed": 25000.00,
    "tegund": "GJOLD",
    "flokkur": "REKSTRARKOSTNADUR"
}
```

#### Fá fjárhagslega samantekt
```bash
GET /api/bokhald/faerslur/samantekt/?fra_dagsetning=2026-01-01&til_dagsetning=2026-03-31
Authorization: Bearer {token}
```

**Svar:**
```json
{
    "timi": {
        "fra": "2026-01-01",
        "til": "2026-03-31"
    },
    "tekjur": 500000.00,
    "gjold": 250000.00,
    "hagnadur": 250000.00,
    "flokkun": {
        "REIKNINGUR": 500000.00,
        "LAUN": 150000.00,
        "EFNISKOSTNADUR": 50000.00,
        "REKSTRARKOSTNADUR": 50000.00
    }
}
```

#### Fá fjárstreymi
```bash
GET /api/bokhald/faerslur/fjarstreymi/?dagar=30
Authorization: Bearer {token}
```

#### Uppfæra mælaborð
```bash
POST /api/bokhald/maelabord/uppfaera/
Authorization: Bearer {token}
```

**Svar:**
```json
{
    "id": 1,
    "notandi": 1,
    "notandi_nafn": "Admin",
    "dagsetning": "2026-03-05",
    "fjoldi_maettra": 15,
    "fjoldi_verkefna_i_vinnslu": 8,
    "fjoldi_verkefna_lokid": 3,
    "heildar_tekjur": 150000.00,
    "heildar_gjold": 50000.00,
    "stofnad": "2026-03-05T10:30:00Z"
}
```

### 6. Super Admin - Kerfiskaupendur

#### Fá alla kerfiskaupendur (SUPER_ADMIN)
```bash
GET /api/bokhald/kerfiskaupendur/
Authorization: Bearer {token}
```

#### Stofna nýjan kerfiskaupanda
```bash
POST /api/bokhald/kerfiskaupendur/
Authorization: Bearer {token}
Content-Type: application/json

{
    "fyrirtaeki_nafn": "Nýtt Fyrirtæki Ehf",
    "kennitala": "6601012340",
    "abyrgdarmaður": "Guðrún Guðrúnardóttir",
    "netfang": "gudrun@nytt.is",
    "simanumer": "5559999",
    "sub_admin_notandi": 5
}
```

## Villumeðhöndlun

### 400 Bad Request
```json
{
    "villa": "Vantar nauðsynlega reiti"
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

## Dæmi um notkun með curl

```bash
# Fá token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"notandanafn":"admin","password":"yourpassword"}'

# Nota token
curl http://localhost:8000/api/starfsfolk/starfsmenn/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1..."
```

## Dæmi um notkun með Python

```python
import requests

# Auðkenning
response = requests.post(
    'http://localhost:8000/api/token/',
    json={'notandanafn': 'admin', 'password': 'yourpassword'}
)
tokens = response.json()
access_token = tokens['access']

# Nota API
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(
    'http://localhost:8000/api/starfsfolk/starfsmenn/',
    headers=headers
)
starfsmenn = response.json()
print(starfsmenn)
```
