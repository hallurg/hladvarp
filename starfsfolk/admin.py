from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Notandi, Starfsmadur, Maeting, Fridagur, 
    Vinnukostnadur, Serhaefi, TimaklukkuTaeki,
    TimaklukkuAtburdur, TimaklukkuLeidretting
)


@admin.register(Notandi)
class NotandiAdmin(BaseUserAdmin):
    list_display = ['notandanafn', 'email', 'fullt_nafn', 'notendategund', 'er_virkur']
    list_filter = ['notendategund', 'er_virkur', 'er_starfsmadur', 'er_admin']
    fieldsets = (
        (None, {'fields': ('notandanafn', 'lykilord')}),
        ('Persónuupplýsingar', {'fields': ('fullt_nafn', 'email', 'simanumer')}),
        ('Réttindi', {
            'fields': ('notendategund', 'er_virkur', 'er_starfsmadur', 'er_admin', 'groups', 'user_permissions'),
        }),
        ('Tími', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('notandanafn', 'email', 'fullt_nafn', 'notendategund', 'lykilord1', 'lykilord2'),
        }),
    )
    search_fields = ['notandanafn', 'email', 'fullt_nafn']
    ordering = ['notandanafn']


@admin.register(Starfsmadur)
class StarfsmadurAdmin(admin.ModelAdmin):
    list_display = ['starfsmannanumer', 'notandi', 'starfstitill', 'rodun', 'kennitala', 'simanumer', 'er_virkur', 'stofnad']
    list_filter = ['er_virkur', 'stofnad']
    search_fields = ['starfsmannanumer', 'notandi__fullt_nafn', 'starfstitill', 'kennitala', 'simanumer']
    readonly_fields = ['starfsmannanumer', 'qr_kodi', 'stofnad', 'uppfaert']
    list_editable = ['rodun']
    ordering = ['rodun', '-stofnad']
    
    fieldsets = (
        ('Grunnupplýsingar', {
            'fields': ('notandi', 'starfsmannanumer', 'starfstitill', 'kennitala', 'heimilisfang', 'simanumer')
        }),
        ('Kerfisupplýsingar', {
            'fields': ('active_directory_notandi', 'qr_kodi')
        }),
        ('Vinnutími', {
            'fields': ('aeskilegur_moettartimi', 'aeskilegur_brottfararstimi')
        }),
        ('Sérhæfing', {
            'fields': ('serhaefi',)
        }),
        ('Staða', {
            'fields': ('er_virkur', 'rodun')
        }),
        ('Tímastimplar', {
            'fields': ('stofnad', 'uppfaert'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Maeting)
class MaetingAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'dagsetning', 'moettartimi', 'brottfararstimi', 'status']
    list_filter = ['status', 'dagsetning']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'starfsmadur__starfsmannanumer']
    date_hierarchy = 'dagsetning'


@admin.register(TimaklukkuTaeki)
class TimaklukkuTaekiAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'device_label', 'status', 'last_seen', 'created_at', 'revoked_at']
    list_filter = ['status', 'created_at', 'revoked_at']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'starfsmadur__starfsmannanumer', 'device_label']
    readonly_fields = ['pairing_code_hash', 'last_seen', 'created_at', 'revoked_at']
    date_hierarchy = 'created_at'


@admin.register(TimaklukkuAtburdur)
class TimaklukkuAtburdurAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'event_type', 'timestamp', 'source', 'client_event_id', 'taeki', 'created_by']
    list_filter = ['event_type', 'source', 'timestamp']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'starfsmadur__starfsmannanumer', 'client_event_id', 'note']
    readonly_fields = [
        'starfsmadur', 'taeki', 'event_type', 'timestamp', 'source',
        'client_event_id', 'raw_payload', 'note', 'created_by'
    ]
    date_hierarchy = 'timestamp'


@admin.register(TimaklukkuLeidretting)
class TimaklukkuLeidrettingAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'status', 'created_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'created_at', 'reviewed_at']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'requested_change', 'reason', 'manager_note']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_by', 'reviewed_at']
    date_hierarchy = 'created_at'


@admin.register(Fridagur)
class FridagurAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'fra_dagsetning', 'til_dagsetning', 'fridags_tegund', 'stada', 'stofnad']
    list_filter = ['stada', 'fridags_tegund', 'fra_dagsetning']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'lysing']
    date_hierarchy = 'fra_dagsetning'


@admin.register(Vinnukostnadur)
class VinnukostnadurAdmin(admin.ModelAdmin):
    list_display = ['starfsmadur', 'dagsetning', 'fjarhaed', 'er_greitt', 'kostnadar_tegund']
    list_filter = ['er_greitt', 'kostnadar_tegund', 'dagsetning']
    search_fields = ['starfsmadur__notandi__fullt_nafn', 'lysing']
    date_hierarchy = 'dagsetning'


@admin.register(Serhaefi)
class SerhaefiAdmin(admin.ModelAdmin):
    list_display = ['heiti', 'lysing']
    search_fields = ['heiti', 'lysing']
