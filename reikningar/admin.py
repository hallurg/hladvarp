from django.contrib import admin
from .models import FasturLidur, Reikningur, ReikningsLidur, Greidsla


@admin.register(FasturLidur)
class FasturLidurAdmin(admin.ModelAdmin):
    list_display = ['heiti', 'fjarhaed', 'er_virkur', 'stofnad']
    list_filter = ['er_virkur']
    search_fields = ['heiti', 'lysing']


@admin.register(Reikningur)
class ReikningurAdmin(admin.ModelAdmin):
    list_display = [
        'reikningsnumer', 'vidskiptavinur', 'reikningsdagsetning',
        'gjalddagi', 'heildarfjarhaed', 'stada', 'er_greiddur'
    ]
    list_filter = ['stada', 'er_greiddur', 'reikningsdagsetning']
    search_fields = ['reikningsnumer', 'vidskiptavinur__nafn']
    readonly_fields = ['reikningsnumer', 'stofnad', 'uppfaert']
    date_hierarchy = 'reikningsdagsetning'


@admin.register(ReikningsLidur)
class ReikningsLidurAdmin(admin.ModelAdmin):
    list_display = ['reikningur', 'lysing', 'magn', 'einingarverð', 'heildarfjarhaed', 'tegund']
    list_filter = ['tegund']
    search_fields = ['reikningur__reikningsnumer', 'lysing']


@admin.register(Greidsla)
class GreidslaAdmin(admin.ModelAdmin):
    list_display = ['reikningur', 'fjarhaed', 'greidsludagsetning', 'greidslu_adferd']
    list_filter = ['greidslu_adferd', 'greidsludagsetning']
    search_fields = ['reikningur__reikningsnumer']
    date_hierarchy = 'greidsludagsetning'
