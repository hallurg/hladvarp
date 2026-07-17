from django.contrib import admin
from django.urls import reverse
from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied
from .models import Faersla, SuperAdminKerfiskaupandi, Maelabord, Bokhaldslykill


def super_admin_dashboard_view(request):
    if not request.user.is_authenticated or request.user.notendategund != 'SUPER_ADMIN':
        raise PermissionDenied('Aðgangur bannaður')

    kerfiskaupendur = SuperAdminKerfiskaupandi.objects.select_related('sub_admin_notandi').order_by('fyrirtaeki_nafn')

    context = admin.site.each_context(request)
    context.update({
        'title': 'Super Admin - Aðgangsstýring',
        'kerfiskaupendur': kerfiskaupendur,
    })
    return TemplateResponse(request, 'admin/super_admin_dashboard.html', context)


_original_get_urls = admin.site.get_urls
_original_get_app_list = admin.site.get_app_list


def _custom_admin_urls():
    custom_urls = [
        path(
            'super-admin/',
            admin.site.admin_view(super_admin_dashboard_view),
            name='super_admin_dashboard'
        ),
    ]
    return custom_urls + _original_get_urls()


def _custom_admin_app_list(request, app_label=None):
    app_list = _original_get_app_list(request, app_label)

    if not request.user.is_authenticated or request.user.notendategund != 'SUPER_ADMIN':
        return app_list

    filtered_app_list = []
    for app in app_list:
        if app.get('app_label') != 'bokhald':
            continue

        allowed_models = [
            model for model in app.get('models', [])
            if model.get('object_name') == 'SuperAdminKerfiskaupandi'
        ]
        if not allowed_models:
            continue

        filtered_app = app.copy()
        filtered_app['models'] = allowed_models
        filtered_app_list.append(filtered_app)

    return filtered_app_list


admin.site.get_urls = _custom_admin_urls
admin.site.get_app_list = _custom_admin_app_list


@admin.register(Bokhaldslykill)
class BokhaldslykillAdmin(admin.ModelAdmin):
    list_display = ['lykilnumer', 'heiti', 'tegund', 'er_virkur', 'stofnad']
    list_filter = ['tegund', 'er_virkur']
    search_fields = ['lykilnumer', 'heiti', 'lysing']
    readonly_fields = ['lykilnumer', 'stofnad', 'uppfaert']


@admin.register(Faersla)
class FaerslaAdmin(admin.ModelAdmin):
    list_display = ['faerslunumer', 'dagsetning', 'lysing', 'bokhaldslykill', 'debet_fjarhaed', 'kredit_fjarhaed', 'tegund']
    list_filter = ['tegund', 'flokkur', 'dagsetning']
    search_fields = ['faerslunumer', 'lysing', 'vidskiptavinur__nafn', 'starfsmadur__notandi__fullt_nafn']
    date_hierarchy = 'dagsetning'
    readonly_fields = ['faerslunumer', 'stofnad']


@admin.register(SuperAdminKerfiskaupandi)
class SuperAdminKerfiskaukandiAdmin(admin.ModelAdmin):
    list_display = [
        'item_id', 'fyrirtaeki_nafn', 'abyrgdarmaður', 'netfang', 'fullt_simanumer',
        'er_virkur', 'stofnad', 'opna_kerfi_hnappur'
    ]
    list_filter = ['er_virkur', 'stofnad']
    search_fields = ['item_id', 'fyrirtaeki_nafn', 'abyrgdarmaður', 'kennitala', 'postnumer', 'sveitarfelag']
    readonly_fields = ['item_id', 'landsnumer']
    fields = [
        'item_id', 'fyrirtaeki_nafn', 'kennitala', 'abyrgdarmaður', 'netfang',
        'heimilisfang', 'postnumer', 'sveitarfelag', 'land', 'landsnumer',
        'simanumer', 'sub_admin_notandi', 'er_virkur', 'athugasemdir'
    ]

    class Media:
        js = ('js/superadmin_kerfiskaupandi_form.js',)

    def opna_kerfi_hnappur(self, obj):
        if not obj.er_virkur or not obj.sub_admin_notandi:
            return '-'

        launch_url = reverse('kerfiskaupandi-opna-kerfi', args=[obj.pk])
        return format_html(
            '<a class="button kn-icon-button" href="{}?redirect=1" target="_blank" rel="noopener"><span class="kn-icon" aria-hidden="true">&#128640;</span> Opna kerfi</a>',
            launch_url,
        )

    opna_kerfi_hnappur.short_description = 'Opna glugga'

    def fullt_simanumer(self, obj):
        return obj.fullt_simanumer

    fullt_simanumer.short_description = 'Símanúmer'


@admin.register(Maelabord)
class MaelabordAdmin(admin.ModelAdmin):
    list_display = [
        'notandi', 'dagsetning', 'fjoldi_maettra', 
        'fjoldi_verkefna_i_vinnslu', 'heildar_tekjur', 'heildar_gjold'
    ]
    list_filter = ['dagsetning']
    search_fields = ['notandi__fullt_nafn']
    date_hierarchy = 'dagsetning'
