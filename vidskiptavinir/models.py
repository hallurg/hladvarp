from django.db import models
import random
import string


class Vidskiptavinur(models.Model):
    """Viðskiptavinabókhald"""
    
    # Persónuupplýsingar
    nafn = models.CharField(max_length=255, verbose_name='Nafn')
    kennitala = models.CharField(max_length=11, unique=True, verbose_name='Kennitala')
    customer_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        verbose_name='Viðskiptavinанúmer'
    )
    
    # Samskiptaupplýsingar
    heimilisfang = models.TextField(verbose_name='Heimilisfang')
    simanumer = models.CharField(max_length=20, verbose_name='Símanúmer')
    netfang = models.EmailField(blank=True, verbose_name='Netfang')
    vsk_numer = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name='VSK númer'
    )
    
    # Fjárhagslegar upplýsingar
    skuldastada = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name='Skuldastaða'
    )
    
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    athugasemdir = models.TextField(blank=True, verbose_name='Athugasemdir')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Viðskiptavinur'
        verbose_name_plural = 'Viðskiptavinir'
        ordering = ['nafn']
    
    def __str__(self):
        return f"{self.nafn} ({self.customer_id})"
    
    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = self.generate_customer_id()
        super().save(*args, **kwargs)
    
    def generate_customer_id(self):
        """Býr til customer ID úr kennitölu"""
        return f"CUST{self.kennitala}"
    
    @property
    def heildar_greidslur(self):
        """Heildarupphæð greiddra reikninga"""
        from reikningar.models import Greidsla
        return sum(
            g.fjarhaed for g in Greidsla.objects.filter(
                reikningur__vidskiptavinur=self
            )
        )
    
    @property
    def utistandandi_reikningar(self):
        """Fjöldi útistandandi reikninga"""
        from reikningar.models import Reikningur
        return Reikningur.objects.filter(
            vidskiptavinur=self,
            er_greiddur=False
        ).count()


class Kerfisnumer(models.Model):
    """Item ID - kerfisnúmer fyrir viðskiptavin"""
    
    vidskiptavinur = models.ForeignKey(
        Vidskiptavinur,
        on_delete=models.CASCADE,
        related_name='kerfisnumer',
        verbose_name='Viðskiptavinur'
    )
    item_id = models.CharField(max_length=50, unique=True, verbose_name='Item ID')
    lysing = models.TextField(blank=True, verbose_name='Lýsing')
    er_virkur = models.BooleanField(default=True, verbose_name='Er virkur')
    
    stofnad = models.DateTimeField(auto_now_add=True, verbose_name='Stofnað')
    uppfaert = models.DateTimeField(auto_now=True, verbose_name='Uppfært')
    
    class Meta:
        verbose_name = 'Kerfisnúmer'
        verbose_name_plural = 'Kerfisnúmer'
        ordering = ['item_id']
    
    def __str__(self):
        return f"{self.item_id} - {self.vidskiptavinur.nafn}"
