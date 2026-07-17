from django.db import models
from django.conf import settings
from vidskiptavinir.models import Vidskiptavinur
from verkefni.models import Verkefni
from starfsfolk.models import Starfsmadur


class FasturLidur(models.Model):
    """Fastir gjaldliðir sem bætast við alla reikninga"""
    
    heiti = models.CharField(max_length=255, verbose_name='Heiti')
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    fjarhaed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Fjárhæð'
    )
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Fastur liður'
        verbose_name_plural = 'Fastir liðir'
        ordering = ['heiti']
    
    def __str__(self):
        return f"{self.heiti} - {self.fjarhaed} kr."


class Reikningur(models.Model):
    """Reikningar fyrir viðskiptavini"""
    
    STADA_VALS = [
        ('DRÖG', 'Drög'),
        ('SENDUR', 'Sendur'),
        ('GREIDDUR', 'Greiddur'),
        ('GJALDFALLIN', 'Gjaldfallin'),
    ]
    
    vidskiptavinur = models.ForeignKey(
        Vidskiptavinur,
        on_delete=models.CASCADE,
        related_name='reikningar',
        verbose_name='Viðskiptavinur'
    )
    reikningsnumer = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        verbose_name='Reikningsnúmer'
    )
    verkefni = models.ForeignKey(
        Verkefni,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reikningar',
        verbose_name='Verkefni'
    )
    
    # Dagsetningar
    reikningsdagsetning = models.DateField(verbose_name='Reikningsdagsetning')
    gjalddagi = models.DateField(verbose_name='Gjalddagi')
    eindagi = models.DateField(null=True, blank=True, verbose_name='Eindagi')
    
    # Upphæðir
    heildarfjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Heildarfjárhæð'
    )
    vsk_fjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='VSK fjárhæð'
    )
    
    stada = models.CharField(
        max_length=20,
        choices=STADA_VALS,
        default='DRÖG',
        verbose_name='Staða'
    )
    er_greiddur = models.BooleanField(default=False, verbose_name='Er greiddur')
    
    athugasemdir = models.TextField(blank=True, verbose_name='Athugasemdir')
    
    stofnad_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Stofnað af'
    )
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Reikningur'
        verbose_name_plural = 'Reikningar'
        ordering = ['-reikningsdagsetning']
    
    def __str__(self):
        return f"Reikningur {self.reikningsnumer} - {self.vidskiptavinur.nafn}"
    
    def save(self, *args, **kwargs):
        if not self.reikningsnumer:
            self.reikningsnumer = self.generate_reikningsnumer()
        super().save(*args, **kwargs)
    
    def generate_reikningsnumer(self):
        """Býr til reikningsnúmer"""
        import datetime
        now = datetime.datetime.now()
        count = Reikningur.objects.filter(
            stofnad__year=now.year,
            stofnad__month=now.month
        ).count() + 1
        return f"INV-{now.year}{now.month:02d}-{count:04d}"
    
    def reikna_heildarfjarhaed(self):
        """Reikna heildarfjárhæð reiknings"""
        total = sum(l.heildarfjarhaed for l in self.lidur.all())
        return total
    
    def reikna_vsk(self):
        """Reikna VSK"""
        vsk_hlutfall = 0.24  # 24% VSK
        return self.heildarfjarhaed * vsk_hlutfall


class ReikningsLidur(models.Model):
    """Liðir á reikningi"""
    
    TEGUND_VALS = [
        ('VINNUKOSTNADUR', 'Vinnukostnaður'),
        ('EFNISKOSTNADUR', 'Efniskostnaður'),
        ('FASTUR_LIDUR', 'Fastur liður'),
        ('ANNAD', 'Annað'),
    ]
    
    reikningur = models.ForeignKey(
        Reikningur,
        on_delete=models.CASCADE,
        related_name='lidur',
        verbose_name='Reikningur'
    )
    lysing = models.CharField(max_length=255, verbose_name='Lýsing')
    magn = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name='Magn'
    )
    einingarverð = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Einingarverð'
    )
    heildarfjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Heildarfjárhæð'
    )
    tegund = models.CharField(
        max_length=20,
        choices=TEGUND_VALS,
        default='ANNAD',
        verbose_name='Tegund'
    )
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Reikningsliður'
        verbose_name_plural = 'Reikningsliðir'
        ordering = ['stofnad']
    
    def __str__(self):
        return f"{self.lysing} - {self.heildarfjarhaed} kr."
    
    def save(self, *args, **kwargs):
        self.heildarfjarhaed = self.magn * self.einingarverð
        super().save(*args, **kwargs)


class Greidsla(models.Model):
    """Greiðslur á reikninga"""
    
    GREIDSLUMATIR = [
        ('MILLIFAERSLA', 'Millifærsla'),
        ('KORT', 'Kort'),
        ('REIDUFÉ', 'Reiðufé'),
        ('ANNAD', 'Annað'),
    ]
    
    reikningur = models.ForeignKey(
        Reikningur,
        on_delete=models.CASCADE,
        related_name='greidslur',
        verbose_name='Reikningur'
    )
    fjarhaed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Fjárhæð'
    )
    greidsludagsetning = models.DateField(verbose_name='Greiðsludagsetning')
    greidslu_adferd = models.CharField(
        max_length=20,
        choices=GREIDSLUMATIR,
        default='MILLIFAERSLA',
        verbose_name='Greiðslumáti'
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
        verbose_name = 'Greiðsla'
        verbose_name_plural = 'Greiðslur'
        ordering = ['-greidsludagsetning']
    
    def __str__(self):
        return f"Greiðsla {self.fjarhaed} kr. - {self.reikningur.reikningsnumer}"
