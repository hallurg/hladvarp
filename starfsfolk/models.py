from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
import hashlib
import random
import secrets
import string


class NotandiManager(BaseUserManager):
    """Manager fyrir sérsniðna notendategun"""
    
    def create_user(self, notandanafn, email, fullt_nafn, password=None, **extra_fields):
        if not notandanafn:
            raise ValueError('Notandi verður að hafa notandanafn')
        if not email:
            raise ValueError('Notandi verður að hafa netfang')

        # Keep backwards compatibility with older call sites using `lykilord`.
        if password is None and 'lykilord' in extra_fields:
            password = extra_fields.pop('lykilord')
        
        email = self.normalize_email(email)
        notandi = self.model(
            notandanafn=notandanafn,
            email=email,
            fullt_nafn=fullt_nafn,
            **extra_fields
        )
        notandi.set_password(password)
        notandi.save(using=self._db)
        return notandi
    
    def create_superuser(self, notandanafn, email, fullt_nafn, password=None, **extra_fields):
        extra_fields.setdefault('er_admin', True)
        extra_fields.setdefault('er_starfsmadur', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('notendategund', 'SUPER_ADMIN')
        
        if extra_fields.get('er_admin') is not True:
            raise ValueError('Superuser verður að hafa er_admin=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser verður að hafa is_superuser=True.')

        return self.create_user(notandanafn, email, fullt_nafn, password, **extra_fields)


class Notandi(AbstractBaseUser, PermissionsMixin):
    """Sérsniðinn notandi með þremur aðgangsstigum"""
    
    NOTENDATEGUNDIR = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('SUB_ADMIN', 'Sub Admin (Yfirmaður)'),
        ('STARFSMADUR', 'Starfsmaður'),
    ]
    
    notandanafn = models.CharField(max_length=150, unique=True, verbose_name='Notandanafn')
    email = models.EmailField(unique=True, verbose_name='Netfang')
    fullt_nafn = models.CharField(max_length=255, verbose_name='Fullt nafn')
    simanumer = models.CharField(max_length=20, blank=True, verbose_name='Símanúmer')
    notendategund = models.CharField(
        max_length=20, 
        choices=NOTENDATEGUNDIR, 
        default='STARFSMADUR',
        verbose_name='Notendategund'
    )
    
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    er_starfsmadur = models.BooleanField(default=False, verbose_name='Er starfsmaður')
    er_admin = models.BooleanField(default=False, verbose_name='Er stjórnandi')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Stofnaður')
    
    objects = NotandiManager()
    
    USERNAME_FIELD = 'notandanafn'
    REQUIRED_FIELDS = ['email', 'fullt_nafn']
    
    class Meta:
        verbose_name = 'Notandi'
        verbose_name_plural = 'Notendur'
    
    def __str__(self):
        return f"{self.fullt_nafn} ({self.notandanafn})"
    
    @property
    def is_staff(self):
        return self.er_admin
    
    @property
    def is_superuser_custom(self):
        return self.notendategund == 'SUPER_ADMIN'
    
    @property
    def is_subadmin(self):
        return self.notendategund == 'SUB_ADMIN'


class Serhaefi(models.Model):
    """Sérhæfing starfsmanna"""
    
    heiti = models.CharField(max_length=100, unique=True, verbose_name='Heiti')
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Sérhæfi'
        verbose_name_plural = 'Sérhæfi'
        ordering = ['heiti']
    
    def __str__(self):
        return self.heiti


class Starfsmadur(models.Model):
    """Starfsmannaupplýsingar með QR kóða"""
    
    notandi = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='starfsmadur_profile',
        verbose_name='Notandi'
    )
    starfsmannanumer = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        verbose_name='Starfsmannanúmer'
    )
    kennitala = models.CharField(max_length=11, unique=True, verbose_name='Kennitala')
    heimilisfang = models.TextField(verbose_name='Heimilisfang')
    simanumer = models.CharField(max_length=20, verbose_name='Símanúmer')
    starfstitill = models.CharField(max_length=255, blank=True, verbose_name='Starfstitill')
    active_directory_notandi = models.CharField(
        max_length=150, 
        blank=True,
        verbose_name='Active Directory notandanafn'
    )
    
    # QR kóði fyrir aðgangsstýringu
    qr_kodi = models.ImageField(
        upload_to='qr_codes/', 
        blank=True, 
        null=True,
        verbose_name='QR kóði'
    )
    
    # Vinnutími
    aeskilegur_moettartimi = models.TimeField(
        null=True, 
        blank=True,
        verbose_name='Æskilegur mætingartími'
    )
    aeskilegur_brottfararstimi = models.TimeField(
        null=True, 
        blank=True,
        verbose_name='Æskilegur brottfarartími'
    )
    
    # Sérhæfing
    serhaefi = models.ManyToManyField(
        Serhaefi, 
        blank=True,
        verbose_name='Sérhæfi'
    )
    
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    rodun = models.PositiveIntegerField(default=0, verbose_name='Röðun')
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Starfsmaður'
        verbose_name_plural = 'Starfsmenn'
        ordering = ['rodun', '-stofnad']
    
    def __str__(self):
        return f"{self.notandi.fullt_nafn} - {self.starfsmannanumer}"
    
    def save(self, *args, **kwargs):
        # Búa til starfsmannanúmer ef það er ekki til
        if not self.starfsmannanumer:
            self.starfsmannanumer = self.generate_starfsmannanumer()
        
        super().save(*args, **kwargs)
        
        # Búa til QR kóða ef hann er ekki til
        if not self.qr_kodi:
            self.generate_qr_code()
    
    def generate_starfsmannanumer(self):
        """Býr til random starfsmannanúmer sem byrjar á fyrirtækisstaf"""
        company_code = settings.COMPANY_CODE
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{company_code}{random_code}"
    
    def generate_qr_code(self):
        """Býr til QR kóða fyrir starfsmann"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f"STAFF:{self.starfsmannanumer}:{self.kennitala}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        file_name = f'qr_{self.starfsmannanumer}.png'
        self.qr_kodi.save(file_name, File(buffer), save=True)


class Maeting(models.Model):
    """Mætingaskráning starfsmanna"""
    
    STATUS_VALS = [
        ('MAETTUR', 'Mættur'),
        ('FJARVERANDI', 'Fjarverandi'),
        ('VEIKUR', 'Veikur'),
        ('FRI', 'Frí'),
        ('UTKALL', 'Útkall'),
    ]
    
    starfsmadur = models.ForeignKey(
        Starfsmadur, 
        on_delete=models.CASCADE,
        related_name='maetingar',
        verbose_name='Starfsmaður'
    )
    dagsetning = models.DateField(verbose_name='Dagsetning')
    moettartimi = models.DateTimeField(null=True, blank=True, verbose_name='Mætingartími')
    brottfararstimi = models.DateTimeField(null=True, blank=True, verbose_name='Brottfarartími')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_VALS, 
        default='FJARVERANDI',
        verbose_name='Staða'
    )
    athugasemdir = models.TextField(blank=True, verbose_name='Athugasemdir')
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Mæting'
        verbose_name_plural = 'Mætingar'
        unique_together = ['starfsmadur', 'dagsetning']
        ordering = ['-dagsetning']
    
    def __str__(self):
        return f"{self.starfsmadur} - {self.dagsetning} ({self.status})"


class TimaklukkuTaeki(models.Model):
    """Device pairing record for the timekeeping flow."""

    STADA_VALS = [
        ('PAIRING', 'Pairing'),
        ('ACTIVE', 'Active'),
        ('REVOKED', 'Revoked'),
    ]

    starfsmadur = models.ForeignKey(
        Starfsmadur,
        on_delete=models.CASCADE,
        related_name='timaklukku_taeki',
        verbose_name='Starfsmaður'
    )
    device_label = models.CharField(max_length=120, blank=True, verbose_name='Tæki')
    pairing_code_hash = models.CharField(max_length=64, blank=True, verbose_name='Pairing code hash')
    status = models.CharField(max_length=20, choices=STADA_VALS, default='PAIRING', verbose_name='Staða')
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='Síðast séð')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    revoked_at = models.DateTimeField(null=True, blank=True, verbose_name='Afturkallað')

    class Meta:
        verbose_name = 'Tímaklukku tæki'
        verbose_name_plural = 'Tímaklukku tæki'
        ordering = ['-created_at']

    def __str__(self):
        label = self.device_label or 'Ónefnt tæki'
        return f"{self.starfsmadur} - {label} ({self.status})"

    @staticmethod
    def hash_pairing_code(code):
        return hashlib.sha256(code.encode('utf-8')).hexdigest()

    @classmethod
    def generate_pairing_code(cls):
        return secrets.token_urlsafe(18)

    def set_pairing_code(self, code):
        self.pairing_code_hash = self.hash_pairing_code(code)

    def matches_pairing_code(self, code):
        if not code or not self.pairing_code_hash:
            return False
        return self.pairing_code_hash == self.hash_pairing_code(code)

    def activate(self):
        self.status = 'ACTIVE'
        self.last_seen = timezone.now()
        self.revoked_at = None
        self.save(update_fields=['status', 'last_seen', 'revoked_at'])

    def revoke(self):
        self.status = 'REVOKED'
        self.revoked_at = timezone.now()
        self.save(update_fields=['status', 'revoked_at'])


class TimaklukkuAtburdur(models.Model):
    """Append-only event log for timekeeping actions."""

    TEGUNDIR = [
        ('IN', 'Clock in'),
        ('OUT', 'Clock out'),
        ('BREAK_START', 'Break start'),
        ('BREAK_END', 'Break end'),
        ('CORRECTION_REQUESTED', 'Correction requested'),
        ('CORRECTION_APPROVED', 'Correction approved'),
        ('CORRECTION_REJECTED', 'Correction rejected'),
        ('DEVICE_CONNECTED', 'Device connected'),
        ('DEVICE_REVOKED', 'Device revoked'),
    ]

    SOURCE_VALS = [
        ('PHONE', 'Phone'),
        ('MOBILE', 'Mobile'),
        ('BIXBY', 'Bixby'),
        ('ADMIN', 'Admin'),
        ('SYSTEM', 'System'),
        ('API', 'API'),
    ]

    starfsmadur = models.ForeignKey(
        Starfsmadur,
        on_delete=models.CASCADE,
        related_name='timaklukku_atburdir',
        verbose_name='Starfsmaður'
    )
    taeki = models.ForeignKey(
        TimaklukkuTaeki,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atburdir',
        verbose_name='Tæki'
    )
    event_type = models.CharField(max_length=30, choices=TEGUNDIR, verbose_name='Tegund')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='Tími')
    source = models.CharField(max_length=20, choices=SOURCE_VALS, default='API', verbose_name='Uppruni')
    client_event_id = models.CharField(
        max_length=120,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Client event ID'
    )
    raw_payload = models.JSONField(default=dict, blank=True, verbose_name='Raw payload')
    note = models.TextField(blank=True, verbose_name='Athugasemd')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timaklukku_atburdir',
        verbose_name='Skráð af'
    )

    class Meta:
        verbose_name = 'Tímaklukku atburður'
        verbose_name_plural = 'Tímaklukku atburðir'
        ordering = ['-timestamp', '-id']

    def __str__(self):
        return f"{self.starfsmadur} - {self.event_type} - {self.timestamp:%Y-%m-%d %H:%M}"


class TimaklukkuLeidretting(models.Model):
    """Employee correction request and manager review workflow."""

    STADA_VALS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    starfsmadur = models.ForeignKey(
        Starfsmadur,
        on_delete=models.CASCADE,
        related_name='timaklukku_leidrettingar',
        verbose_name='Starfsmaður'
    )
    maeting = models.ForeignKey(
        Maeting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timaklukku_leidrettingar',
        verbose_name='Mæting'
    )
    requested_change = models.TextField(verbose_name='Óskuð leiðrétting')
    reason = models.TextField(blank=True, verbose_name='Ástæða')
    status = models.CharField(max_length=20, choices=STADA_VALS, default='PENDING', verbose_name='Staða')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timaklukku_leidrettingar_yfirfarnar',
        verbose_name='Yfirfarið af'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Yfirfarið')
    manager_note = models.TextField(blank=True, verbose_name='Athugasemd stjórnanda')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Uppfært')

    class Meta:
        verbose_name = 'Tímaklukku leiðrétting'
        verbose_name_plural = 'Tímaklukku leiðréttingar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.starfsmadur} - {self.status}"

    def approve(self, user, note=''):
        self.status = 'APPROVED'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.manager_note = note
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'manager_note', 'updated_at'])

    def reject(self, user, note=''):
        self.status = 'REJECTED'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.manager_note = note
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'manager_note', 'updated_at'])


class Fridagur(models.Model):
    """Frídagaumsóknir"""
    
    FRIDAGS_TEGUNDIR = [
        ('ORLOF', 'Orlof'),
        ('VEIKINDI', 'Veikindi'),
        ('ANNAÐ', 'Annað'),
    ]
    
    STADA_VALS = [
        ('OBIDINN', 'Óbíðinn'),
        ('SAMTHYKKTUR', 'Samþykktur'),
        ('SYNJAD', 'Synjað'),
    ]
    
    starfsmadur = models.ForeignKey(
        Starfsmadur, 
        on_delete=models.CASCADE,
        related_name='fridagar',
        verbose_name='Starfsmaður'
    )
    fra_dagsetning = models.DateField(verbose_name='Frá dagsetningu')
    til_dagsetning = models.DateField(verbose_name='Til dagsetningar')
    fridags_tegund = models.CharField(
        max_length=20, 
        choices=FRIDAGS_TEGUNDIR,
        verbose_name='Tegund'
    )
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    stada = models.CharField(
        max_length=20, 
        choices=STADA_VALS, 
        default='OBIDINN',
        verbose_name='Staða'
    )
    samthykkt_af = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='samthykktir_fridagar',
        verbose_name='Samþykkt af'
    )
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Frídagur'
        verbose_name_plural = 'Frídagar'
        ordering = ['-fra_dagsetning']
    
    def __str__(self):
        return f"{self.starfsmadur} - {self.fra_dagsetning} til {self.til_dagsetning}"


class Vinnukostnadur(models.Model):
    """Vinnukostnaður starfsmanna"""
    
    KOSTNADAR_TEGUNDIR = [
        ('LAUN', 'Laun'),
        ('YFIRVINNUTIME', 'Yfirvinnustundir'),
        ('EFNISKOSTNADUR', 'Efniskostnaður'),
        ('ANNAD', 'Annað'),
    ]
    
    starfsmadur = models.ForeignKey(
        Starfsmadur, 
        on_delete=models.CASCADE,
        related_name='vinnukostnadur',
        verbose_name='Starfsmaður'
    )
    dagsetning = models.DateField(verbose_name='Dagsetning')
    fjarhaed = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Fjárhæð'
    )
    kostnadar_tegund = models.CharField(
        max_length=20, 
        choices=KOSTNADAR_TEGUNDIR,
        verbose_name='Tegund kostnaðar'
    )
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    er_greitt = models.BooleanField(default=False, verbose_name='Er greitt')
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    
    class Meta:
        verbose_name = 'Vinnukostnaður'
        verbose_name_plural = 'Vinnukostnaður'
        ordering = ['-dagsetning']
    
    def __str__(self):
        return f"{self.starfsmadur} - {self.fjarhaed} kr. ({self.dagsetning})"
