from django.contrib import admin
from .models import Vidskiptavinur, Kerfisnumer


@admin.register(Vidskiptavinur)
class VidskiptavinurAdmin(admin.ModelAdmin):
    list_display = ['nafn', 'customer_id', 'kennitala', 'simanumer', 'skuldastada', 'er_virkur']
    list_filter = ['er_virkur', 'stofnad']
    search_fields = ['nafn', 'kennitala', 'customer_id', 'simanumer']
    readonly_fields = ['customer_id', 'stofnad', 'uppfaert', 'heildar_greidslur', 'utistandandi_reikningar']
    
    fieldsets = (
        ('Grunnupplýsingar', {
            'fields': ('nafn', 'kennitala', 'customer_id')
        }),
        ('Samskiptaupplýsingar', {
            'fields': ('heimilisfang', 'simanumer', 'netfang', 'vsk_numer')
        }),
        ('Fjárhagur', {
            'fields': ('skuldastada', 'heildar_greidslur', 'utistandandi_reikningar')
        }),
        ('Annað', {
            'fields': ('er_virkur', 'athugasemdir')
        }),
        ('Tímastimplar', {
            'fields': ('stofnad', 'uppfaert'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Kerfisnumer)
class KerfisnumerAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'vidskiptavinur', 'lysing', 'er_virkur']
    list_filter = ['er_virkur', 'stofnad']
    search_fields = ['item_id', 'vidskiptavinur__nafn', 'lysing']
