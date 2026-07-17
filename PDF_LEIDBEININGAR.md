# PDF Skýrslur - Leiðbeiningar

## Yfirlit

Kerfið getur búið til PDF skýrslur úr öllum valmyndum. Allar PDF skýrslur nota litapalletu Kaupfjelag Nærsveitamanna með appelsínugulum haus og hvítum bakgrunni.

## Tiltækar PDF skýrslur

### 1. Starfsmannaskrá

**Endpoint:**
```bash
GET /api/starfsfolk/starfsmenn/export_pdf/
Authorization: Bearer {token}
```

**Innihald:**
- Starfsmannanúmer
- Nafn
- Kennitala
- Símanúmer
- Staða (Virkur/Óvirkur)

**Notkun:**
Notaðu þetta til að fá yfirlit yfir alla starfsmenn til prentun eða skjalavörslu.

---

### 2. Mætingaskrá

**Endpoint:**
```bash
GET /api/starfsfolk/maetingar/export_pdf/?fra_dagsetning=2026-03-01&til_dagsetning=2026-03-31
Authorization: Bearer {token}
```

**Innihald:**
- Dagsetning
- Starfsmaður
- Mætingartími
- Brottfarartími
- Staða

**Notkun:**
Notaðu til að útbúa mætingaskýrslur fyrir launaútreikninga eða yfirlit.

---

### 3. Viðskiptavinaskrá

**Endpoint:**
```bash
GET /api/vidskiptavinir/export_pdf/
Authorization: Bearer {token}
```

**Innihald:**
- Customer ID
- Nafn
- Kennitala
- Símanúmer
- Skuldastaða

**Notkun:**
Til að fá yfirlit yfir alla viðskiptavini og skuldir þeirra.

---

### 4. Verkefnalisti

**Endpoint:**
```bash
GET /api/verkefni/export_pdf/
Authorization: Bearer {token}
```

**Innihald:**
- Titill verkefnis
- Starfsmaður
- Staða
- Deadline
- Framvinda (%)

**Notkun:**
Til að fylgjast með stöðu verkefna og gefa yfirmanni yfirlit.

---

### 5. Reikningalisti

**Endpoint:**
```bash
GET /api/reikningar/export_pdf/
Authorization: Bearer {token}
```

**Innihald:**
- Reikningsnúmer
- Viðskiptavinur
- Dagsetning
- Gjalddagi
- Fjárhæð
- Staða

**Notkun:**
Til að fá yfirlit yfir alla reikninga, útistandandi og greidda.

---

### 6. Bókhaldsfærslur

**Endpoint:**
```bash
GET /api/bokhald/faerslur/export_pdf/?fra_dagsetning=2026-01-01&til_dagsetning=2026-12-31
Authorization: Bearer {token}
```

**Innihald:**
- Færslunúmer
- Dagsetning
- Lýsing
- Bókhaldslykill
- Debet
- Kredit
- Samtals

**Notkun:**
Til að fá yfirlit yfir allar bókhaldsfærslur á tilteknu tímabili.

---

### 7. Bókhaldslyklar

**Endpoint:**
```bash
GET /api/bokhald/bokhaldslyklar/export_pdf/
Authorization: Bearer {token}
```

**Innihald:**
- Lykilnúmer
- Heiti
- Tegund
- Staða

**Notkun:**
Til að fá yfirlit yfir alla bókhaldslykla og stöðu þeirra.

---

### 8. Ársreikningur

**Endpoint:**
```bash
GET /api/bokhald/faerslur/arsreikningur/?ar=2026
Authorization: Bearer {token}
```

**Innihald:**
- **Rekstrarreikningur**:
  - Tekjur
  - Gjöld
  - Hagnaður/Tap
- **Efnahagsreikningur**:
  - Eignir
  - Skuldir
  - Eigið fé

**Notkun:**
Til að búa til formlegan ársreikning fyrir endurskoðanda eða skattyfirvöld.

---

## Hvernig á að nota PDF endpoints

### Með curl:

```bash
# Fá access token
TOKEN=$(curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"notandanafn":"admin","password":"yourpassword"}' \
  | jq -r '.access')

# Sækja PDF
curl http://localhost:8000/api/starfsfolk/starfsmenn/export_pdf/ \
  -H "Authorization: Bearer $TOKEN" \
  -o starfsmannaskra.pdf
```

### Með Python:

```python
import requests

# Auðkenning
response = requests.post(
    'http://localhost:8000/api/token/',
    json={'notandanafn': 'admin', 'password': 'yourpassword'}
)
token = response.json()['access']

# Sækja PDF
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/starfsfolk/starfsmenn/export_pdf/',
    headers=headers
)

# Vista PDF
with open('starfsmannaskra.pdf', 'wb') as f:
    f.write(response.content)
```

### Með JavaScript/Frontend:

```javascript
// Sækja token
const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        notandanafn: 'admin',
        password: 'yourpassword'
    })
});
const data = await response.json();
const token = data.access;

// Sækja og opna PDF
const pdfResponse = await fetch('http://localhost:8000/api/starfsfolk/starfsmenn/export_pdf/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});

const blob = await pdfResponse.blob();
const url = window.URL.createObjectURL(blob);
window.open(url);
```

## PDF Útlit

Allar PDF skýrslur nota sama útlitið:

### Litir:
- **Haus töflu**: Appelsínugulur (#D97525) með svörtu letri
- **Bakgrunnur**: Hvítur
- **Texti**: Svartur
- **Borðar**: Grár

### Skipulag:
1. **Titill**: Stór blár titill efst
2. **Dagsetning**: Dagsetning stofnunar neðst við titil
3. **Tafla**: Skipulögð tafla með gögnum
4. **Samtölur**: Ef við á (t.d. í bókhaldsfærslum)

## Sérstök atriði

### Tímabil
Margar skýrslur taka við tímabil sem parameter:
```bash
?fra_dagsetning=2026-01-01&til_dagsetning=2026-12-31
```

### Síun
Sumar skýrslur leyfa síun:
```bash
# Aðeins virkir starfsmenn
GET /api/starfsfolk/starfsmenn/virkir/

# Útistandandi reikningar
GET /api/reikningar/utistandandi/
```

### Stærð skráa
PDF skýrslur eru venjulega 50-500 KB eftir magni gagna.

## Ábendingar

1. **Notaðu tímabil**: Takmarkaðu gögn með tímabili til að halda PDF smærri
2. **Vista staðsetning**: Vistaðu PDF í skipulagðar möppur (t.d. `skyrslur/2026/mars/`)
3. **Sjálfvirkar skýrslur**: Notaðu Celery tasks til að búa til sjálfvirkar mánaðarlegar skýrslur
4. **Email sending**: Sendu PDF sem viðhengi í email til viðskiptavina

## Villur

### 401 Unauthorized
Þú þarft gilt access token. Endurnýjaðu token ef nauðsyn krefur.

### 403 Forbidden
Notandi hefur ekki réttindi. Aðeins SUB_ADMIN og SUPER_ADMIN geta búið til flestar skýrslur.

### 404 Not Found
Engin gögn fundust fyrir valið tímabil eða síu.

## Framtíðarbætingar

Í næstu útgáfum verður bætt við:
- Email sending beint frá API
- Branding með lógói
- Aðlaganlegt útlit
- Excel export
- Bulk PDF generation
- Scheduled reports (dagleg/vikuleg/mánaðarleg)

## Dæmi um notkunartilfelli

### Tilfelli 1: Mánaðarleg launayfirlit
```bash
# Hver mánaður - exporta mætingar
GET /api/starfsfolk/maetingar/export_pdf/?fra_dagsetning=2026-03-01&til_dagsetning=2026-03-31
```

### Tilfelli 2: Ársreikningar
```bash
# Í árslok
GET /api/bokhald/faerslur/arsreikningur/?ar=2026
```

### Tilfelli 3: Vikuleg verkefnayfirlit
```bash
# Á hverjum mánudegi
GET /api/verkefni/export_pdf/
```

## Stuðningur

Fyrir vandamál eða spurningar um PDF skýrslur, hafðu samband við þróunarteymið.
