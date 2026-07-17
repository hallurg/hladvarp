from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from vidskiptavinir.models import Vidskiptavinur
from starfsfolk.models import Starfsmadur
import random
import string


class Bokhaldslykill(models.Model):
    """Bókhaldslyklar - Chart of Accounts"""
    
    TEGUND_VALS = [
        ('EIGNIR', 'Eignir'),
        ('SKULDIR', 'Skuldir'),
        ('EIGID_FE', 'Eigið fé'),
        ('TEKJUR', 'Tekjur'),
        ('GJOLD', 'Gjöld'),
    ]
    
    lykilnumer = models.CharField(max_length=10, unique=True, verbose_name='Lykilnúmer')
    heiti = models.CharField(max_length=255, verbose_name='Heiti')
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    tegund = models.CharField(
        max_length=20,
        choices=TEGUND_VALS,
        verbose_name='Tegund'
    )
    yfirlykilnumer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='undirlykilar',
        verbose_name='Yfirlykill'
    )
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Bókhaldslykill'
        verbose_name_plural = 'Bókhaldslyklar'
        ordering = ['lykilnumer']
    
    def __str__(self):
        return f"{self.lykilnumer} - {self.heiti}"
    
    @property
    def staða(self):
        """Reikna stöðu á lykli"""
        faerslur = self.faerslur.all()
        debet = sum(f.debet_fjarhaed for f in faerslur)
        kredit = sum(f.kredit_fjarhaed for f in faerslur)
        return debet - kredit


class Faersla(models.Model):
    """Færslur í bókhaldi"""

    TEGUND_VALS = [
        ('TEKJUR', 'Tekjur'),
        ('GJOLD', 'Gjöld'),
    ]

    FLOKKUR_VALS = [
        ('REIKNINGUR', 'Reikningur'),
        ('LAUN', 'Laun'),
        ('EFNISKOSTNADUR', 'Efniskostnaður'),
        ('REKSTRARKOSTNADUR', 'Rekstrarkostnaður'),
        ('ANNAD', 'Annað'),
    ]

    faerslunumer = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Færslunúmer'
    )
    dagsetning = models.DateField(verbose_name='Dagsetning')
    lysing = models.CharField(max_length=255, verbose_name='Lýsing')

    # Bókhaldslyklar - debet og kredit
    bokhaldslykill = models.ForeignKey(
        Bokhaldslykill,
        on_delete=models.PROTECT,
        related_name='faerslur',
        verbose_name='Bókhaldslykill'
    )
    debet_fjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Debet fjárhæð'
    )
    kredit_fjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Kredit fjárhæð'
    )

    # Gamli kerfið fyrir afturvirkt samhæfi
    fjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Fjárhæð'
    )
    tegund = models.CharField(
        max_length=20,
        choices=TEGUND_VALS,
        verbose_name='Tegund'
    )
    flokkur = models.CharField(
        max_length=30,
        choices=FLOKKUR_VALS,
        verbose_name='Flokkur'
    )

    # Tengingar
    vidskiptavinur = models.ForeignKey(
        Vidskiptavinur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faerslur',
        verbose_name='Viðskiptavinur'
    )
    starfsmadur = models.ForeignKey(
        Starfsmadur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faerslur',
        verbose_name='Starfsmaður'
    )

    athugasemdir = models.TextField(blank=True, verbose_name='Athugasemdir')

    skrad_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Skráð af'
    )
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')

    class Meta:
        verbose_name = 'Færsla'
        verbose_name_plural = 'Færslur'
        ordering = ['-dagsetning']

    def __str__(self):
        return f"{self.faerslunumer} - {self.lysing} ({self.dagsetning})"

    def save(self, *args, **kwargs):
        if not self.faerslunumer:
            self.faerslunumer = self.generate_faerslunumer()
        if not self.fjarhaed:
            self.fjarhaed = self.debet_fjarhaed or self.kredit_fjarhaed
        super().save(*args, **kwargs)

    def generate_faerslunumer(self):
        """Býr til færslunúmer"""
        import datetime
        now = datetime.datetime.now()
        count = Faersla.objects.filter(
            stofnad__year=now.year,
            stofnad__month=now.month
        ).count() + 1
        return f"F-{now.year}{now.month:02d}-{count:04d}"


class SuperAdminKerfiskaupandi(models.Model):
    """Skrá yfir fyrirtæki sem kaupa kerfið (fyrir Super Admin)"""

    ITEM_ID_PREFIX = 'KD-W-'
    ITEM_ID_SUFFIX_LENGTH = 11
    POSTNUMER_SVEITARFELAG_MAP = {
        '101': 'Reykjavik',
        '102': 'Reykjavik',
        '103': 'Reykjavik',
        '104': 'Reykjavik',
        '105': 'Reykjavik',
        '107': 'Reykjavik',
        '108': 'Reykjavik',
        '109': 'Reykjavik',
        '110': 'Reykjavik',
        '111': 'Reykjavik',
        '112': 'Reykjavik',
        '113': 'Reykjavik',
        '116': 'Reykjavik',
        '170': 'Seltjarnarnes',
        '190': 'Vogar',
        '200': 'Kopavogur',
        '201': 'Kopavogur',
        '203': 'Kopavogur',
        '210': 'Gardabaer',
        '220': 'Hafnarfjordur',
        '221': 'Hafnarfjordur',
        '225': 'Gardabaer',
        '230': 'Reykjanesbaer',
        '232': 'Reykjanesbaer',
        '233': 'Reykjanesbaer',
        '240': 'Grindavik',
        '245': 'Sandgerdi',
        '250': 'Gardur',
        '260': 'Reykjanesbaer',
        '270': 'Mosfellsbaer',
        '300': 'Akranes',
        '310': 'Borgarnes',
        '320': 'Reykholt',
        '340': 'Stykkisholmur',
        '400': 'Isafjordur',
        '500': 'Stadarskali',
        '550': 'Saudarkrokur',
        '600': 'Akureyri',
        '603': 'Akureyri',
        '610': 'Grenivik',
        '640': 'Husavik',
        '700': 'Egilsstadir',
        '710': 'Seydisfjordur',
        '730': 'Reydarfjordur',
        '735': 'Eskifjordur',
        '740': 'Neskaupstadur',
        '750': 'Faskrudsfjordur',
        '760': 'Breiddalsvik',
        '780': 'Hofn',
        '800': 'Selfoss',
        '810': 'Hveragerdi',
        '815': 'Thorlakshofn',
        '820': 'Eyrarbakki',
        '825': 'Stokkseyri',
        '840': 'Laugarvatn',
        '850': 'Hella',
        '860': 'Hvolsvollur',
        '870': 'Vik',
        '900': 'Vestmannaeyjar',
    }
    LAND_SIMAREGLUR = {
        'Island': {'landsnumer': '+354', 'min_len': 7, 'max_len': 7},
        'Danmork': {'landsnumer': '+45', 'min_len': 8, 'max_len': 8},
        'Noregur': {'landsnumer': '+47', 'min_len': 8, 'max_len': 8},
        'Sviþjod': {'landsnumer': '+46', 'min_len': 7, 'max_len': 13},
        'Finnland': {'landsnumer': '+358', 'min_len': 7, 'max_len': 12},
        'Bandarikin': {'landsnumer': '+1', 'min_len': 10, 'max_len': 10},
        'Kanada': {'landsnumer': '+1', 'min_len': 10, 'max_len': 10},
        'Bretland': {'landsnumer': '+44', 'min_len': 9, 'max_len': 10},
        'Thyskaland': {'landsnumer': '+49', 'min_len': 7, 'max_len': 13},
        'Frakkland': {'landsnumer': '+33', 'min_len': 9, 'max_len': 9},
        'Spann': {'landsnumer': '+34', 'min_len': 9, 'max_len': 9},
        'Poland': {'landsnumer': '+48', 'min_len': 9, 'max_len': 9},
    }
    LAND_VALS = [(land, land) for land in LAND_SIMAREGLUR.keys()]
    
    fyrirtaeki_nafn = models.CharField(max_length=255, verbose_name='Nafn fyrirtækis')
    item_id = models.CharField(
        max_length=16,
        unique=True,
        blank=True,
        editable=False,
        verbose_name='Item ID'
    )
    kennitala = models.CharField(max_length=11, unique=True, verbose_name='Kennitala')
    abyrgdarmaður = models.CharField(max_length=255, verbose_name='Ábyrgðarmaður')
    netfang = models.EmailField(verbose_name='Netfang')
    heimilisfang = models.CharField(max_length=255, blank=True, verbose_name='Heimilisfang')
    postnumer = models.CharField(max_length=10, blank=True, verbose_name='Póstnúmer')
    sveitarfelag = models.CharField(max_length=120, blank=True, verbose_name='Sveitarfélag')
    land = models.CharField(max_length=120, choices=LAND_VALS, default='Island', verbose_name='Land')
    landsnumer = models.CharField(max_length=6, blank=True, verbose_name='Landsnúmer')
    simanumer = models.CharField(max_length=20, verbose_name='Símanúmer')
    
    # Tengdur sub-admin notandi
    sub_admin_notandi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kerfiskaupandi',
        verbose_name='Sub-admin notandi'
    )
    
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    athugasemdir = models.TextField(blank=True, verbose_name='Athugasemdir')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Kerfiskaupandi'
        verbose_name_plural = 'Kerfiskaupendur'
        ordering = ['fyrirtaeki_nafn']
    
    def __str__(self):
        return f"{self.fyrirtaeki_nafn} - {self.abyrgdarmaður}"

    @classmethod
    def generate_item_id(cls):
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=cls.ITEM_ID_SUFFIX_LENGTH))
        return f"{cls.ITEM_ID_PREFIX}{suffix}"

    @staticmethod
    def _digits_only(value):
        return ''.join(ch for ch in str(value or '') if ch.isdigit())

    def clean(self):
        self.fyrirtaeki_nafn = (self.fyrirtaeki_nafn or '').strip()
        self.abyrgdarmaður = (self.abyrgdarmaður or '').strip()
        self.heimilisfang = (self.heimilisfang or '').strip()
        self.sveitarfelag = (self.sveitarfelag or '').strip()
        self.land = (self.land or 'Island').strip()

        kennitala_digits = self._digits_only(self.kennitala)
        if len(kennitala_digits) != 10:
            raise ValidationError({'kennitala': 'Kennitala þarf að vera 10 tölustafir (XXXXXX-XXXX).'})
        self.kennitala = f"{kennitala_digits[:6]}-{kennitala_digits[6:]}"

        self.postnumer = self._digits_only(self.postnumer)

        if self.land in self.LAND_SIMAREGLUR:
            regla = self.LAND_SIMAREGLUR[self.land]
            self.landsnumer = regla['landsnumer']

        if self.land == 'Island':
            if self.postnumer in self.POSTNUMER_SVEITARFELAG_MAP:
                self.sveitarfelag = self.POSTNUMER_SVEITARFELAG_MAP[self.postnumer]
        elif not self.sveitarfelag:
            self.sveitarfelag = ''

        sima_digits = self._digits_only(self.simanumer)
        if not sima_digits:
            raise ValidationError({'simanumer': 'Símanúmer má aðeins innihalda tölustafi.'})

        if self.land in self.LAND_SIMAREGLUR:
            regla = self.LAND_SIMAREGLUR[self.land]
            if not (regla['min_len'] <= len(sima_digits) <= regla['max_len']):
                if regla['min_len'] == regla['max_len']:
                    msg = f"Símanúmer fyrir {self.land} þarf að vera {regla['min_len']} tölustafir."
                else:
                    msg = (
                        f"Símanúmer fyrir {self.land} þarf að vera á bilinu "
                        f"{regla['min_len']}-{regla['max_len']} tölustafir."
                    )
                raise ValidationError({'simanumer': msg})

        self.simanumer = sima_digits

    @property
    def fullt_simanumer(self):
        if self.landsnumer:
            return f"{self.landsnumer} {self.simanumer}".strip()
        return self.simanumer

    def save(self, *args, **kwargs):
        if not self.item_id:
            while True:
                candidate = self.generate_item_id()
                if not SuperAdminKerfiskaupandi.objects.filter(item_id=candidate).exists():
                    self.item_id = candidate
                    break

        self.full_clean()

        super().save(*args, **kwargs)


class Maelabord(models.Model):
    """Mælaborð fyrir virkni og tölfræði"""
    
    notandi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Notandi'
    )
    dagsetning = models.DateField(verbose_name='Dagsetning')
    
    # Tölfræði
    fjoldi_maettra = models.IntegerField(default=0, verbose_name='Fjöldi mættra')
    fjoldi_verkefna_i_vinnslu = models.IntegerField(default=0, verbose_name='Verkefni í vinnslu')
    fjoldi_verkefna_lokid = models.IntegerField(default=0, verbose_name='Verkefni lokið')
    heildar_tekjur = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Heildar tekjur'
    )
    heildar_gjold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Heildar gjöld'
    )
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Mælaborð'
        verbose_name_plural = 'Mælaborð'
        unique_together = ['notandi', 'dagsetning']
        ordering = ['-dagsetning']
    
    def __str__(self):
        return f"Mælaborð {self.notandi} - {self.dagsetning}"
