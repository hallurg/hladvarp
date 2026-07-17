# Bókhaldslyklar - Leiðbeiningar

## Hvað eru bókhaldslyklar?

Bókhaldslyklar (Chart of Accounts) eru grunnurinn að bókhaldinu. Þeir flokka allar fjárhagslegar færslur í skipulega flokka, alveg eins og í DK, Navision, SAP og öðrum bókhaldskerfum.

## Lykiltegundir

Kerfið styður 5 megintegundir bókhaldslykla:

### 1. EIGNIR (1xxx)
Allt sem fyrirtækið á
- **1110** - Handbært fé
- **1120** - Bankareikningar
- **1510** - Kröfur á viðskiptavini
- **1810** - Tæki og tól
- **1820** - Ökutæki

### 2. SKULDIR (2xxx)
Allt sem fyrirtækið skuldar
- **2410** - Skuldir við birgja
- **2710** - VSK skuld
- **2720** - Staðgreiðsla skatts

### 3. EIGIÐ FÉ (3xxx)
Eigið fé fyrirtækisins
- **3100** - Hlutafé
- **3900** - Óráðstafað eigið fé

### 4. TEKJUR (4xxx)
Allar tekjur fyrirtækisins
- **4110** - Þjónustutekjur
- **4900** - Aðrar tekjur

### 5. GJÖLD (5xxx-8xxx)
Allur kostnaður fyrirtækisins
- **5110** - Hráefni og vörur
- **6110** - Föst laun
- **6120** - Yfirvinnugreiðslur
- **7110** - Húsaleiga
- **7210** - Eldsneyti
- **7410** - Auglýsingar

## Stofna staðlaða bókhaldslykla

Þegar þú setur upp kerfið í fyrsta skipti, keyrðu þessa skipun:

```bash
POST /api/bokhald/bokhaldslyklar/stofna_stadar_lykla/
Authorization: Bearer {token}
```

Þetta býr til alla staðlaða lyklana sjálfkrafa.

## Hvernig á að nota bókhaldslykla?

### Dæmi 1: Skrá sölu
```json
POST /api/bokhald/faerslur/
{
    "dagsetning": "2026-03-05",
    "lysing": "Sala til Viðskiptavinar X",
    "bokhaldslykill": 5,  // 4110 - Þjónustutekjur
    "debet_fjarhaed": 0,
    "kredit_fjarhaed": 50000,
    "tegund": "TEKJUR",
    "flokkur": "REIKNINGUR"
}
```

### Dæmi 2: Skrá launagreiðslu
```json
POST /api/bokhald/faerslur/
{
    "dagsetning": "2026-03-05",
    "lysing": "Laun mars 2026",
    "bokhaldslykill": 12,  // 6110 - Föst laun
    "debet_fjarhaed": 150000,
    "kredit_fjarhaed": 0,
    "tegund": "GJOLD",
    "flokkur": "LAUN",
    "starfsmadur": 3
}
```

### Dæmi 3: Skrá efniskaup
```json
POST /api/bokhald/faerslur/
{
    "dagsetning": "2026-03-05",
    "lysing": "Kaup á verkfærum",
    "bokhaldslykill": 8,  // 5110 - Hráefni og vörur
    "debet_fjarhaed": 25000,
    "kredit_fjarhaed": 0,
    "tegund": "GJOLD",
    "flokkur": "EFNISKOSTNADUR"
}
```

## Debet og Kredit

### Debet (vinstri hlið)
- Hækkar EIGNIR
- Hækkar GJÖLD
- Lækkar SKULDIR
- Lækkar EIGIÐ FÉ
- Lækkar TEKJUR

### Kredit (hægri hlið)
- Lækkar EIGNIR
- Lækkar GJÖLD
- Hækkar SKULDIR
- Hækkar EIGIÐ FÉ
- Hækkar TEKJUR

## API Endpoints fyrir bókhaldslykla

### Skoða alla lykla
```bash
GET /api/bokhald/bokhaldslyklar/
```

### Skoða lykla eftir tegund
```bash
GET /api/bokhald/bokhaldslyklar/eftir_tegund/?tegund=TEKJUR
```

### Skoða stöðu einstaks lykils
```bash
GET /api/bokhald/bokhaldslyklar/{id}/stada_yfirlits/
```

**Svar:**
```json
{
    "lykill": {
        "lykilnumer": "4110",
        "heiti": "Þjónustutekjur",
        "tegund": "TEKJUR"
    },
    "heildar_debet": 0,
    "heildar_kredit": 500000.00,
    "stada": -500000.00,
    "fjoldi_faerslna": 25
}
```

### Exporta lykla sem PDF
```bash
GET /api/bokhald/bokhaldslyklar/export_pdf/
```

## Skoða færslur á lykli

```bash
GET /api/bokhald/faerslur/?bokhaldslykill=5
```

## Búa til ársreikning

```bash
GET /api/bokhald/faerslur/arsreikningur/?ar=2026
```

Þetta býr til PDF með:
- Rekstrarreikningi (tekjur - gjöld = hagnaður)
- Efnahagsreikningi (eignir - skuldir = eigið fé)

## Gott að vita

### Jafnvægisregla
Í hverri færslu þarf debet og kredit að vera jöfn. Ef þú skráir 50.000 kr. í debet, þarf 50.000 kr. í kredit líka.

### Dæmi um heilstæða færslu
Þegar viðskiptavinur greiðir reikning:

**Færsla 1**: Hækka bankareikning (eignir)
```json
{
    "bokhaldslykill": 2,  // 1120 - Bankareikningar
    "debet_fjarhaed": 50000,
    "kredit_fjarhaed": 0
}
```

**Færsla 2**: Lækka viðskiptakröfur (eignir)
```json
{
    "bokhaldslykill": 6,  // 1510 - Kröfur á viðskiptavini
    "debet_fjarhaed": 0,
    "kredit_fjarhaed": 50000
}
```

## Tengingar við önnur kerfi

### Sjálfvirk skráning frá reikningakerfinu
Þegar reikningur er stofnaður, býr kerfið sjálfkrafa til færslur í bókhaldslyklana:
- Kredit á tekjulykil (4110)
- Debet á viðskiptakröfur (1510)

### Tengingar við launakerfi
Launagreiðslur úr starfsmannakerfinu skrást sjálfkrafa á launalykla (6xxx).

## Ábendingar

1. **Upphafsstaða**: Settu upp upphafsstaðu þegar þú byrjar að nota kerfið
2. **Mánaðarleg uppgjör**: Gerðu uppgjör í lok hvers mánaðar
3. **Öryggisafrit**: Taktu reglulega öryggisafrit af bókhaldinu
4. **Endurskoðun**: Láttu endurskoðanda yfirfara bókhaldið reglulega

## Stuðningur

Ef þú hefur spurningar um bókhaldslyklana, hafðu samband við kerfisstjóra.
