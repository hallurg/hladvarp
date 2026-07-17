# Uppsetningarleiðbeiningar - Kaupfjelag Nærsveitamanna Stjórnunarkerfi

## 1. Nauðsynleg hugbúnaður

### PostgreSQL gagnagrunnur
1. Sækja og setja upp PostgreSQL frá https://www.postgresql.org/download/windows/
2. Búa til nýjan gagnagrunn:
```sql
CREATE DATABASE kaupfjelag_db;
CREATE USER postgres WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE kaupfjelag_db TO postgres;
```

### Python
1. Sækja Python 3.11 eða nýrra frá https://www.python.org/downloads/
2. Passa að velja "Add Python to PATH" við uppsetningu

### Redis (fyrir Celery)
1. Sækja Redis fyrir Windows frá https://github.com/tporadowski/redis/releases
2. Keyra redis-server.exe

## 2. Setja upp verkefnið

### Opna PowerShell í verkefnamöppunni

```powershell
cd "c:\Users\Notandi\Documents\New project"
```

### Búa til virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Setja upp Python pakka

```powershell
pip install -r requirements.txt
```

### Búa til .env skrá

Afrita .env.example yfir í .env og breyta gildum:

```powershell
Copy-Item .env.example .env
```

Opna .env og breyta:
```
SECRET_KEY=generate-new-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=kaupfjelag_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Company Settings
COMPANY_CODE=KN
```

### Keyra gagnagrunnsfærslur

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Búa til Super Admin notanda

```powershell
python manage.py createsuperuser
```

Fylgja leiðbeiningum:
- Notandanafn: admin
- Netfang: admin@kaupfjelag.is
- Fullt nafn: Super Administrator
- Lykilorð: [þitt örugga lykilorð]

### Búa til nauðsynlegar möppur

```powershell
New-Item -ItemType Directory -Force -Path "media"
New-Item -ItemType Directory -Force -Path "media\qr_codes"
New-Item -ItemType Directory -Force -Path "media\verkefni_skrar"
New-Item -ItemType Directory -Force -Path "static"
New-Item -ItemType Directory -Force -Path "staticfiles"
```

### Safna static skrám

```powershell
python manage.py collectstatic --noinput
```

## 3. Keyra þróunarserverinn

```powershell
python manage.py runserver
```

Kerfið ætti nú að vera aðgengilegt á: http://localhost:8000

## 4. Admin viðmót

Fara á: http://localhost:8000/admin/

Skrá inn með super admin notanda sem þú bjóst til.

## 5. API Endpoints

### Authentication
- POST `/api/token/` - Fá JWT token
- POST `/api/token/refresh/` - Endurnýja token

### Starfsfólk
- GET/POST `/api/starfsfolk/starfsmenn/` - Starfsmannalisti
- GET `/api/starfsfolk/maetingar/maetiyfirlit_dagsins/` - Mætingar dagsins
- POST `/api/starfsfolk/maetingar/stimplast_inn/` - Stimpla inn
- POST `/api/starfsfolk/maetingar/stimplast_ut/` - Stimpla út
- GET/POST `/api/starfsfolk/fridagar/` - Frídagabeiðnir

### Viðskiptavinir
- GET/POST `/api/vidskiptavinir/` - Viðskiptavinaskrá
- GET `/api/vidskiptavinir/{id}/fjarhagur/` - Fjárhagsupplýsingar

### Verkefni
- GET/POST `/api/verkefni/verkbeidnir/` - Verkbeiðnir
- GET/POST `/api/verkefni/` - Verkefni
- GET `/api/verkefni/min_verkefni/` - Mín verkefni
- POST `/api/verkefni/{id}/byrja/` - Byrja verkefni
- POST `/api/verkefni/{id}/ljuka/` - Ljúka verkefni

### Reikningar
- GET/POST `/api/reikningar/` - Reikningar
- GET `/api/reikningar/utistandandi/` - Útistandandi reikningar
- POST `/api/reikningar/{id}/senda/` - Senda reikning

### Bókhald
- GET/POST `/api/bokhald/faerslur/` - Bókhaldsfærslur
- GET `/api/bokhald/faerslur/samantekt/` - Fjárhagsleg samantekt
- GET `/api/bokhald/maelabord/` - Mælaborð
- POST `/api/bokhald/maelabord/uppfaera/` - Uppfæra mælaborð

## 6. Celery (fyrir bakgrunnsverkefni)

Opna nýjan terminal og keyra:

```powershell
.\venv\Scripts\activate
celery -A kaupfjelag_kerfi worker -l info
```

## 7. Prófunargögn

Þú getur búið til prófunargögn í Django shell:

```powershell
python manage.py shell
```

```python
from starfsfolk.models import Notandi, Starfsmadur, Serhaefi
from vidskiptavinir.models import Vidskiptavinur

# Búa til sérhæfi
serhaefi = Serhaefi.objects.create(heiti="Rafvirkjun", lysing="Rafvirkjaþjónusta")

# Búa til starfsmann
notandi = Notandi.objects.create_user(
    notandanafn="jondoe",
    email="jon@example.com",
    fullt_nafn="Jón Dóe",
    lykilord="password123",
    notendategund="STARFSMADUR",
    er_starfsmadur=True
)

starfsmadur = Starfsmadur.objects.create(
    notandi=notandi,
    kennitala="0101012345",
    heimilisfang="Testgata 1, Reykjavík",
    simanumer="5551234"
)
starfsmadur.serhaefi.add(serhaefi)

# Búa til viðskiptavin
vidskiptavinur = Vidskiptavinur.objects.create(
    nafn="Test Ehf",
    kennitala="5501012340",
    heimilisfang="Fyrirtækjagata 10, Reykjavík",
    simanumer="5555678",
    netfang="test@example.is"
)

print("Prófunargögn búin til!")
```

## 8. Algengar villur og lausnir

### Villa: "No module named 'psycopg2'"
**Lausn:** `pip install psycopg2-binary`

### Villa: "Connection refused" fyrir gagnagrunn
**Lausn:** Athuga að PostgreSQL sé í gangi og að tengigögn í .env séu rétt

### Villa: QR kóðar birtast ekki
**Lausn:** Athuga að media möppur séu til og að MEDIA_ROOT sé rétt stillt

### Villa: Static files virka ekki
**Lausn:** Keyra `python manage.py collectstatic`

## 9. Öryggisatriði fyrir framleiðslu

Þegar kerfið fer í framleiðslu:

1. Breyta `DEBUG=False` í .env
2. Búa til sterkt SECRET_KEY
3. Setja rétt ALLOWED_HOSTS
4. Nota HTTPS
5. Setja upp öruggan gagnagrunnslykil
6. Nota öruggan vefþjón (Gunicorn/Nginx)
7. Setja upp varnir (Firewall, etc.)
8. Taka reglulegar öryggisafrit

## 10. Næstu skref

- Setja upp email þjónustu fyrir áminningar
- Útfæra PDF útskrift fyrir reikninga
- Bæta við skýrsluvirkni
- Útfæra frontend með React eða Vue.js
- Setja upp móbílapp fyrir QR skanna

## Hjálp og stuðningur

Fyrir spurningar eða hjálp, hafðu samband við þróunarteymið.
