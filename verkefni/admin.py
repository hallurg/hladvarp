from django.contrib import admin
from .models import (
    Verkbeiðni, Verkefni, VerkefniSkra, 
    VerkefniAthugasemd, DeadlineAminnning
)


@admin.register(Verkbeiðni)
class VerkbeidniAdmin(admin.ModelAdmin):
    list_display = ['titill', 'vidskiptavinur', 'forgangur', 'stada', 'stofnad']
    list_filter = ['stada', 'forgangur', 'stofnad']
    search_fields = ['titill', 'lysing', 'vidskiptavinur__nafn']
    readonly_fields = ['stofnad', 'uppfaert']


@admin.register(Verkefni)
class VerkefniAdmin(admin.ModelAdmin):
    list_display = ['titill', 'starfsmadur', 'rodun', 'stada', 'vinnustadur', 'deadline', 'stofnad']
    list_filter = ['stada', 'vinnustadur', 'stofnad']
    search_fields = ['titill', 'lysing', 'starfsmadur__notandi__fullt_nafn']
    readonly_fields = ['stofnad', 'uppfaert', 'progress_percent']
    list_editable = ['rodun']
    ordering = ['rodun', '-stofnad']
    date_hierarchy = 'deadline'


@admin.register(VerkefniSkra)
class VerkefniSkraAdmin(admin.ModelAdmin):
    list_display = ['verkefni', 'tegund', 'lysing', 'upphlad_af', 'upphlad']
    list_filter = ['tegund', 'upphlad']
    search_fields = ['verkefni__titill', 'lysing']


@admin.register(VerkefniAthugasemd)
class VerkefniAthugasemdAdmin(admin.ModelAdmin):
    list_display = ['verkefni', 'notandi', 'athugasemd', 'stofnad']
    list_filter = ['stofnad']
    search_fields = ['verkefni__titill', 'athugasemd']


@admin.register(DeadlineAminnning)
class DeadlineAminnningAdmin(admin.ModelAdmin):
    list_display = ['verkefni', 'aminntar_dagar_fyrir', 'send_aminningu', 'aminningu_send']
    list_filter = ['send_aminningu', 'aminningu_send']
    search_fields = ['verkefni__titill']
