from django.db import models
from django.conf import settings
from starfsfolk.models import Starfsmadur
from vidskiptavinir.models import Vidskiptavinur


class Verkbeiðni(models.Model):
    """Verkbeiðnakerfi"""
    
    STADA_VALS = [
        ('OBIDINN', 'Óbíðinn'),
        ('SAMTHYKKTUR', 'Samþykktur'),
        ('I_VINNSLU', 'Í vinnslu'),
        ('LOKID', 'Lokið'),
        ('SYNJAD', 'Synjað'),
    ]
    
    FORGANGUR_VALS = [
        ('LAGUR', 'Lágur'),
        ('MIDLUNGS', 'Miðlungs'),
        ('HEIUR', 'Háur'),
        ('BRADALAST', 'Bráðalast'),
    ]
    
    vidskiptavinur = models.ForeignKey(
        Vidskiptavinur,
        on_delete=models.CASCADE,
        related_name='verkbeidnir',
        verbose_name='Viðskiptavinur'
    )
    titill = models.CharField(max_length=255, verbose_name='Titill')
    lysing = models.TextField(verbose_name='Lýsing')
    forgangur = models.CharField(
        max_length=20,
        choices=FORGANGUR_VALS,
        default='MIDLUNGS',
        verbose_name='Forgangur'
    )
    stada = models.CharField(
        max_length=20,
        choices=STADA_VALS,
        default='OBIDINN',
        verbose_name='Staða'
    )
    
    stofnad_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stofnadar_verkbeidnir',
        verbose_name='Stofnað af'
    )
    samthykkt_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='samthykktar_verkbeidnir',
        verbose_name='Samþykkt af'
    )
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Verkbeiðni'
        verbose_name_plural = 'Verkbeiðnir'
        ordering = ['-stofnad']
    
    def __str__(self):
        return f"{self.titill} - {self.vidskiptavinur.nafn}"


class Verkefni(models.Model):
    """Verkefni sem úthlutað er á starfsmenn"""
    
    STADA_VALS = [
        ('OBIDINN', 'Óbíðinn'),
        ('I_VINNSLU', 'Í vinnslu'),
        ('LOKID', 'Lokið'),
        ('A_HOLD', 'Á biðstöðu'),
    ]
    
    VINNUSTADUR_VALS = [
        ('VINNUSTADUR', 'Vinnustaður'),
        ('UTKALL', 'Útkall'),
    ]
    
    verkbeidni = models.ForeignKey(
        Verkbeiðni,
        on_delete=models.CASCADE,
        related_name='verkefni',
        verbose_name='Verkbeiðni'
    )
    starfsmadur = models.ForeignKey(
        Starfsmadur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verkefni',
        verbose_name='Starfsmaður'
    )
    titill = models.CharField(max_length=255, verbose_name='Titill')
    lysing = models.TextField(verbose_name='Lýsing')
    stada = models.CharField(
        max_length=20,
        choices=STADA_VALS,
        default='OBIDINN',
        verbose_name='Staða'
    )
    vinnustadur = models.CharField(
        max_length=20,
        choices=VINNUSTADUR_VALS,
        default='VINNUSTADUR',
        verbose_name='Vinnustaður'
    )
    
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Deadline')
    rodun = models.PositiveIntegerField(default=0, verbose_name='Röðun')
    
    uthlutad_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uthlutud_verkefni',
        verbose_name='Úthlutað af'
    )
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    lokad = models.DateTimeField(null=True, blank=True, verbose_name='Lokað')
    
    class Meta:
        verbose_name = 'Verkefni'
        verbose_name_plural = 'Verkefni'
        ordering = ['rodun', '-stofnad']
    
    def __str__(self):
        return f"{self.titill} - {self.starfsmadur}"
    
    @property
    def progress_percent(self):
        """Reikna framvindu verkefnis"""
        if self.stada == 'LOKID':
            return 100
        elif self.stada == 'I_VINNSLU':
            return 50
        return 0


class VerkefniSkra(models.Model):
    """Skrár og skjámyndir tengdar verkefni"""
    
    TEGUND_VALS = [
        ('SKJAMYND', 'Skjámynd'),
        ('SKJAL', 'Skjal'),
        ('ANNAD', 'Annað'),
    ]
    
    verkefni = models.ForeignKey(
        Verkefni,
        on_delete=models.CASCADE,
        related_name='skrar',
        verbose_name='Verkefni'
    )
    skra = models.FileField(upload_to='verkefni_skrar/', verbose_name='Skrá')
    tegund = models.CharField(
        max_length=20,
        choices=TEGUND_VALS,
        default='SKJAL',
        verbose_name='Tegund'
    )
    lysing = models.CharField(max_length=255, blank=True, verbose_name='Lýsing')
    
    upphlad_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Hlaðið upp af'
    )
    upphlad = models.DateTimeField(auto_now_add=True, verbose_name='Hlaðið upp')
    
    class Meta:
        verbose_name = 'Verkefnisskrá'
        verbose_name_plural = 'Verkefnisskrár'
        ordering = ['-upphlad']
    
    def __str__(self):
        return f"{self.verkefni.titill} - {self.skra.name}"


class VerkefniAthugasemd(models.Model):
    """Athugasemdir og uppfærslur á verkefnum"""
    
    verkefni = models.ForeignKey(
        Verkefni,
        on_delete=models.CASCADE,
        related_name='athugasemdir',
        verbose_name='Verkefni'
    )
    notandi = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Notandi'
    )
    athugasemd = models.TextField(verbose_name='Athugasemd')
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Athugasemd'
        verbose_name_plural = 'Athugasemdir'
        ordering = ['-stofnad']
    
    def __str__(self):
        return f"{self.verkefni.titill} - {self.notandi}"


class DeadlineAminnning(models.Model):
    """Áminningar um deadline verkefna"""
    
    verkefni = models.ForeignKey(
        Verkefni,
        on_delete=models.CASCADE,
        related_name='aminningar',
        verbose_name='Verkefni'
    )
    aminntar_dagar_fyrir = models.IntegerField(
        default=1,
        verbose_name='Dagar fyrir deadline'
    )
    send_aminningu = models.BooleanField(default=False, verbose_name='Senda áminingu')
    aminningu_send = models.DateTimeField(null=True, blank=True, verbose_name='Áminning send')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Deadline áminnning'
        verbose_name_plural = 'Deadline áminningar'
        ordering = ['-stofnad']
    
    def __str__(self):
        return f"{self.verkefni.titill} - {self.aminntar_dagar_fyrir} dögum fyrir"
