from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.shortcuts import redirect
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum, Q
from urllib.parse import urlsplit
import logging
import uuid
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Permission
from .models import Faersla, SuperAdminKerfiskaupandi, Maelabord, Bokhaldslykill
from .serializers import (
    FaerslaSerializer, SuperAdminKerfiskaukandiSerializer,
    MaelabordSerializer, BokhaldslykillSerializer
)
from starfsfolk.permissions import IsSuperAdmin, IsSubAdminOrSuperAdmin
from .pdf_utils import generate_bokhald_pdf, generate_arsreikningur_pdf


logger = logging.getLogger(__name__)


class BokhaldslykillViewSet(viewsets.ModelViewSet):
    queryset = Bokhaldslykill.objects.all()
    serializer_class = BokhaldslykillSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def eftir_tegund(self, request):
        """Fá bókhaldslykla flokkaða eftir tegund"""
        tegund = request.query_params.get('tegund')
        if tegund:
            lyklar = self.queryset.filter(tegund=tegund, er_virkur=True)
        else:
            lyklar = self.queryset.filter(er_virkur=True)
        
        serializer = self.get_serializer(lyklar, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stada_yfirlits(self, request, pk=None):
        """Fá yfirlit yfir stöðu bókhaldslykils"""
        lykill = self.get_object()
        faerslur = lykill.faerslur.all()
        
        heildar_debet = sum(f.debet_fjarhaed for f in faerslur)
        heildar_kredit = sum(f.kredit_fjarhaed for f in faerslur)
        stada = heildar_debet - heildar_kredit
        
        return Response({
            'lykill': self.get_serializer(lykill).data,
            'heildar_debet': float(heildar_debet),
            'heildar_kredit': float(heildar_kredit),
            'stada': float(stada),
            'fjoldi_faerslna': faerslur.count()
        })
    
    @action(detail=False, methods=['post'])
    def stofna_stadar_lykla(self, request):
        """Búa til staðlaða bókhaldslykla (eins og í DK)"""
        stadar_lyklar = [
            # EIGNIR (1xxx)
            {'lykilnumer': '1000', 'heiti': 'EIGNIR', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1100', 'heiti': 'Veltufjármunir', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1110', 'heiti': 'Handbært fé', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1120', 'heiti': 'Bankareikningar', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1500', 'heiti': 'Viðskiptakröfur', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1510', 'heiti': 'Kröfur á viðskiptavini', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1800', 'heiti': 'Fastafjármunir', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1810', 'heiti': 'Tæki og tól', 'tegund': 'EIGNIR'},
            {'lykilnumer': '1820', 'heiti': 'Ökutæki', 'tegund': 'EIGNIR'},
            
            # SKULDIR (2xxx)
            {'lykilnumer': '2000', 'heiti': 'SKULDIR', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2100', 'heiti': 'Skammtímaskuldir', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2400', 'heiti': 'Viðskiptaskuldir', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2410', 'heiti': 'Skuldir við birgja', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2700', 'heiti': 'Skattar og gjöld', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2710', 'heiti': 'VSK skuld', 'tegund': 'SKULDIR'},
            {'lykilnumer': '2720', 'heiti': 'Staðgreiðsla skatts', 'tegund': 'SKULDIR'},
            
            # EIGIÐ FÉ (3xxx)
            {'lykilnumer': '3000', 'heiti': 'EIGIÐ FÉ', 'tegund': 'EIGID_FE'},
            {'lykilnumer': '3100', 'heiti': 'Hlutafé', 'tegund': 'EIGID_FE'},
            {'lykilnumer': '3900', 'heiti': 'Óráðstafað eigið fé', 'tegund': 'EIGID_FE'},
            
            # TEKJUR (4xxx)
            {'lykilnumer': '4000', 'heiti': 'TEKJUR', 'tegund': 'TEKJUR'},
            {'lykilnumer': '4100', 'heiti': 'Sölutekjur', 'tegund': 'TEKJUR'},
            {'lykilnumer': '4110', 'heiti': 'Þjónustutekjur', 'tegund': 'TEKJUR'},
            {'lykilnumer': '4900', 'heiti': 'Aðrar tekjur', 'tegund': 'TEKJUR'},
            
            # GJÖLD (5xxx-8xxx)
            {'lykilnumer': '5000', 'heiti': 'BEINN KOSTNAÐUR', 'tegund': 'GJOLD'},
            {'lykilnumer': '5100', 'heiti': 'Efniskostnaður', 'tegund': 'GJOLD'},
            {'lykilnumer': '5110', 'heiti': 'Hráefni og vörur', 'tegund': 'GJOLD'},
            
            {'lykilnumer': '6000', 'heiti': 'LAUN', 'tegund': 'GJOLD'},
            {'lykilnumer': '6100', 'heiti': 'Laun og launatengd gjöld', 'tegund': 'GJOLD'},
            {'lykilnumer': '6110', 'heiti': 'Föst laun', 'tegund': 'GJOLD'},
            {'lykilnumer': '6120', 'heiti': 'Yfirvinnugreiðslur', 'tegund': 'GJOLD'},
            {'lykilnumer': '6200', 'heiti': 'Launatengd gjöld', 'tegund': 'GJOLD'},
            {'lykilnumer': '6210', 'heiti': 'Tryggingagjald', 'tegund': 'GJOLD'},
            
            {'lykilnumer': '7000', 'heiti': 'ANNAR REKSTRARKOSTNAÐUR', 'tegund': 'GJOLD'},
            {'lykilnumer': '7100', 'heiti': 'Húsnæðiskostnaður', 'tegund': 'GJOLD'},
            {'lykilnumer': '7110', 'heiti': 'Húsaleiga', 'tegund': 'GJOLD'},
            {'lykilnumer': '7200', 'heiti': 'Ökutækjakostnaður', 'tegund': 'GJOLD'},
            {'lykilnumer': '7210', 'heiti': 'Eldsneyti', 'tegund': 'GJOLD'},
            {'lykilnumer': '7220', 'heiti': 'Viðhald ökutækja', 'tegund': 'GJOLD'},
            {'lykilnumer': '7300', 'heiti': 'Skrifstofukostnaður', 'tegund': 'GJOLD'},
            {'lykilnumer': '7310', 'heiti': 'Skrifstofurekstrarvörur', 'tegund': 'GJOLD'},
            {'lykilnumer': '7320', 'heiti': 'Símagjöld', 'tegund': 'GJOLD'},
            {'lykilnumer': '7400', 'heiti': 'Markaðskostnaður', 'tegund': 'GJOLD'},
            {'lykilnumer': '7410', 'heiti': 'Auglýsingar', 'tegund': 'GJOLD'},
            
            {'lykilnumer': '8000', 'heiti': 'FJÁRMUNATEKJUR/-GJÖLD', 'tegund': 'GJOLD'},
            {'lykilnumer': '8100', 'heiti': 'Vaxtatekjur', 'tegund': 'TEKJUR'},
            {'lykilnumer': '8200', 'heiti': 'Vaxtagjöld', 'tegund': 'GJOLD'},
        ]
        
        stofnad = 0
        for lykill_data in stadar_lyklar:
            lykill, created = Bokhaldslykill.objects.get_or_create(
                lykilnumer=lykill_data['lykilnumer'],
                defaults={
                    'heiti': lykill_data['heiti'],
                    'tegund': lykill_data['tegund'],
                    'er_virkur': True
                }
            )
            if created:
                stofnad += 1
        
        return Response({
            'stofnad': stofnad,
            'skilaboð': f'{stofnad} bókhaldslyklar stofnaðir'
        })
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exporta bókhaldslykla sem PDF"""
        lyklar = self.queryset.filter(er_virkur=True).order_by('lykilnumer')
        
        from .pdf_utils import generate_pdf
        gogn = [[l.lykilnumer, l.heiti, l.get_tegund_display(), f"{l.stada:,.2f} kr."] 
                for l in lyklar]
        dalkur_heiti = ['Lykilnúmer', 'Heiti', 'Tegund', 'Staða']
        
        return generate_pdf('Bókhaldslyklar', gogn, dalkur_heiti, 'bokhaldslyklar.pdf')


class FaerslaViewSet(viewsets.ModelViewSet):
    queryset = Faersla.objects.select_related(
        'vidskiptavinur', 'starfsmadur__notandi', 'skrad_af'
    )
    serializer_class = FaerslaSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    def perform_create(self, serializer):
        serializer.save(skrad_af=self.request.user)
    
    @action(detail=False, methods=['get'])
    def samantekt(self, request):
        """Fá fjárhagslega samantekt"""
        fra_dags = request.query_params.get('fra_dagsetning')
        til_dags = request.query_params.get('til_dagsetning')
        
        queryset = self.queryset
        
        if fra_dags:
            queryset = queryset.filter(dagsetning__gte=fra_dags)
        if til_dags:
            queryset = queryset.filter(dagsetning__lte=til_dags)
        
        tekjur = queryset.filter(tegund='TEKJUR').aggregate(
            heildar=Sum('fjarhaed')
        )['heildar'] or 0
        
        gjold = queryset.filter(tegund='GJOLD').aggregate(
            heildar=Sum('fjarhaed')
        )['heildar'] or 0
        
        hagnadur = tekjur - gjold
        
        # Flokkun eftir tegund
        flokkun = {}
        for flokkur in queryset.values('flokkur').distinct():
            flokkur_nafn = flokkur['flokkur']
            fjarhaed = queryset.filter(flokkur=flokkur_nafn).aggregate(
                heildar=Sum('fjarhaed')
            )['heildar'] or 0
            flokkun[flokkur_nafn] = float(fjarhaed)
        
        return Response({
            'timi': {
                'fra': fra_dags,
                'til': til_dags
            },
            'tekjur': float(tekjur),
            'gjold': float(gjold),
            'hagnadur': float(hagnadur),
            'flokkun': flokkun
        })
    
    @action(detail=False, methods=['get'])
    def fjarstreymi(self, request):
        """Fá fjárstreymi inn og út"""
        dagar = int(request.query_params.get('dagar', 30))
        fra_dags = timezone.now().date() - timedelta(days=dagar)
        
        faerslur = self.queryset.filter(dagsetning__gte=fra_dags).order_by('dagsetning')
        
        # Flokka eftir dögum
        daga_gogn = {}
        for faersla in faerslur:
            dagur = str(faersla.dagsetning)
            if dagur not in daga_gogn:
                daga_gogn[dagur] = {'tekjur': 0, 'gjold': 0}
            
            if faersla.tegund == 'TEKJUR':
                daga_gogn[dagur]['tekjur'] += float(faersla.fjarhaed)
            else:
                daga_gogn[dagur]['gjold'] += float(faersla.fjarhaed)
        
        return Response({
            'timi': f'Síðustu {dagar} dagar',
            'gogn': daga_gogn
        })
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exporta bókhaldsfærslur sem PDF"""
        fra_dags = request.query_params.get('fra_dagsetning')
        til_dags = request.query_params.get('til_dagsetning')
        
        queryset = self.queryset
        if fra_dags:
            queryset = queryset.filter(dagsetning__gte=fra_dags)
        if til_dags:
            queryset = queryset.filter(dagsetning__lte=til_dags)
        
        faerslur = queryset.select_related('bokhaldslykill').order_by('dagsetning')
        return generate_bokhald_pdf(faerslur)
    
    @action(detail=False, methods=['get'])
    def arsreikningur(self, request):
        """Búa til ársreikning"""
        ar = int(request.query_params.get('ar', timezone.now().year))
        
        faerslur = self.queryset.filter(
            dagsetning__year=ar
        ).select_related('bokhaldslykill')
        
        # Reikna tekjur
        tekjur = sum(
            f.kredit_fjarhaed for f in faerslur 
            if f.bokhaldslykill.tegund == 'TEKJUR'
        )
        
        # Reikna gjöld
        gjold = sum(
            f.debet_fjarhaed for f in faerslur 
            if f.bokhaldslykill.tegund == 'GJOLD'
        )
        
        # Reikna eignir
        eignir = sum(
            f.debet_fjarhaed - f.kredit_fjarhaed for f in faerslur 
            if f.bokhaldslykill.tegund == 'EIGNIR'
        )
        
        # Reikna skuldir
        skuldir = sum(
            f.kredit_fjarhaed - f.debet_fjarhaed for f in faerslur 
            if f.bokhaldslykill.tegund == 'SKULDIR'
        )
        
        return generate_arsreikningur_pdf(ar, tekjur, gjold, eignir, skuldir)


class SuperAdminKerfiskaukandiViewSet(viewsets.ModelViewSet):
    queryset = SuperAdminKerfiskaupandi.objects.select_related('sub_admin_notandi')
    serializer_class = SuperAdminKerfiskaukandiSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def _resolve_launch_target_url(self, request):
        target_url = (
            request.query_params.get('redirect_url')
            or getattr(settings, 'SUPERADMIN_LAUNCH_URL', '/admin/')
        )

        # Relative paths are always accepted.
        if target_url.startswith('/'):
            return target_url

        parsed = urlsplit(target_url)
        if parsed.scheme not in ['http', 'https'] or not parsed.hostname:
            return '/admin/'

        allowed_hosts = set(getattr(settings, 'SUPERADMIN_ALLOWED_REDIRECT_HOSTS', []))
        allowed_hosts.add(request.get_host().split(':')[0])

        if parsed.hostname not in allowed_hosts:
            return '/admin/'

        return target_url

    def _build_launch_payload(self, request, kerfiskaupandi, sub_admin, access_token, refresh_token):
        return {
            'access_token': str(access_token),
            'refresh_token': str(refresh_token),
            'kerfiskaupandi': {
                'id': kerfiskaupandi.id,
                'fyrirtaeki_nafn': kerfiskaupandi.fyrirtaeki_nafn,
            },
            'session_user': {
                'id': sub_admin.id,
                'notandanafn': sub_admin.notandanafn,
                'fullt_nafn': sub_admin.fullt_nafn,
                'notendategund': sub_admin.notendategund,
            },
            'opnad_af': {
                'id': request.user.id,
                'notandanafn': request.user.notandanafn,
            }
        }

    def _ensure_sub_admin_permissions(self, sub_admin):
        """Grant practical admin permissions for tenant launch if missing."""
        app_labels = ['starfsfolk', 'verkefni', 'vidskiptavinir', 'reikningar', 'bokhald']

        if not sub_admin.er_admin:
            sub_admin.er_admin = True
        if not sub_admin.er_starfsmadur:
            sub_admin.er_starfsmadur = True
        if not sub_admin.er_virkur:
            sub_admin.er_virkur = True
        sub_admin.save(update_fields=['er_admin', 'er_starfsmadur', 'er_virkur'])

        existing_count = sub_admin.user_permissions.filter(content_type__app_label__in=app_labels).count()
        if existing_count > 0 or sub_admin.is_superuser:
            return

        perms = Permission.objects.filter(content_type__app_label__in=app_labels)
        sub_admin.user_permissions.add(*perms)
    
    @action(detail=False, methods=['get'])
    def virkir(self, request):
        """Fá virka kerfiskaupendur"""
        virkir = self.queryset.filter(er_virkur=True)
        serializer = self.get_serializer(virkir, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='opna-kerfi')
    def opna_kerfi(self, request, pk=None):
        """Búa til one-time launch code svo Super Admin geti opnað kerfi kaupanda í sér glugga."""
        kerfiskaupandi = self.get_object()

        if not kerfiskaupandi.er_virkur:
            return Response(
                {'villa': 'Kerfiskaupandi er óvirkur.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not kerfiskaupandi.sub_admin_notandi:
            return Response(
                {'villa': 'Enginn sub-admin notandi er tengdur þessum kerfiskaupanda.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sub_admin = kerfiskaupandi.sub_admin_notandi
        if sub_admin.notendategund != 'SUB_ADMIN' or not sub_admin.er_virkur:
            return Response(
                {'villa': 'Tengdur sub-admin þarf að vera virkur notandi af tegundinni SUB_ADMIN.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(sub_admin)
        access = refresh.access_token
        access['opnad_af_super_admin_id'] = request.user.id
        access['opnad_af_super_admin_notandanafn'] = request.user.notandanafn
        access['kerfiskaupandi_id'] = kerfiskaupandi.id
        access['launch_mode'] = 'super_admin_window'

        target_url = self._resolve_launch_target_url(request)
        launch_payload = self._build_launch_payload(
            request=request,
            kerfiskaupandi=kerfiskaupandi,
            sub_admin=sub_admin,
            access_token=access,
            refresh_token=refresh,
        )

        delivery_mode = request.query_params.get('delivery', 'code')
        code_ttl = int(getattr(settings, 'SUPERADMIN_LAUNCH_CODE_TTL_SECONDS', 90))

        separator = '&' if '?' in target_url else '?'
        if delivery_mode == 'token':
            # Backwards compatible mode for clients that still consume token from URL.
            launch_url = (
                f"{target_url}{separator}access_token={str(access)}"
                f"&launch_mode=super_admin_window"
                f"&kerfiskaupandi_id={kerfiskaupandi.id}"
            )
            launch_code = None
        else:
            launch_code = uuid.uuid4().hex
            cache.set(f'superadmin_launch:{launch_code}', launch_payload, timeout=code_ttl)
            launch_url = (
                f"{target_url}{separator}launch_code={launch_code}"
                f"&launch_mode=super_admin_window"
                f"&kerfiskaupandi_id={kerfiskaupandi.id}"
            )

        logger.info(
            'super_admin_open_system super_admin_id=%s sub_admin_id=%s kerfiskaupandi_id=%s ip=%s user_agent=%s',
            request.user.id,
            sub_admin.id,
            kerfiskaupandi.id,
            request.META.get('REMOTE_ADDR', ''),
            request.META.get('HTTP_USER_AGENT', ''),
        )

        # Browser/admin launch path: switch Django session to the target sub-admin
        # and redirect directly. This makes the admin UI open with the expected role.
        if request.query_params.get('redirect') in ['1', 'true', 'True'] and delivery_mode == 'code':
            self._ensure_sub_admin_permissions(sub_admin)
            auth_login(request, sub_admin, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(target_url)

        if request.query_params.get('redirect') in ['1', 'true', 'True']:
            return redirect(launch_url)

        response_data = {
            'launch_url': launch_url,
            'delivery': delivery_mode,
            **launch_payload,
        }
        if launch_code:
            response_data['launch_code'] = launch_code
            response_data['launch_code_expires_in'] = code_ttl

        return Response(response_data)

    @action(
        detail=False,
        methods=['post'],
        url_path='consume-launch-code',
        permission_classes=[AllowAny],
        authentication_classes=[]
    )
    def consume_launch_code(self, request):
        """Skipta one-time launch code í session tokens fyrir opnaðan glugga."""
        launch_code = request.data.get('launch_code')
        if not launch_code:
            return Response(
                {'villa': 'launch_code vantar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache_key = f'superadmin_launch:{launch_code}'
        payload = cache.get(cache_key)
        if not payload:
            return Response(
                {'villa': 'launch_code er ógildur eða útrunninn.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cache.delete(cache_key)
        return Response(payload)


class MaelabordViewSet(viewsets.ModelViewSet):
    queryset = Maelabord.objects.select_related('notandi')
    serializer_class = MaelabordSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def dagsetning(self, request):
        """Fá mælaborð fyrir tiltekna dagsetningu"""
        dagsetning = request.query_params.get('dagsetning', timezone.now().date())
        
        try:
            maelabord = self.queryset.get(
                notandi=request.user,
                dagsetning=dagsetning
            )
            serializer = self.get_serializer(maelabord)
            return Response(serializer.data)
        except Maelabord.DoesNotExist:
            return Response(
                {'villa': 'Mælaborð fannst ekki'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def uppfaera(self, request):
        """Uppfæra mælaborð fyrir í dag"""
        dagur = timezone.now().date()
        
        from starfsfolk.models import Maeting
        from verkefni.models import Verkefni
        
        # Telja mætingar
        fjoldi_maettra = Maeting.objects.filter(
            dagsetning=dagur,
            status='MAETTUR'
        ).count()
        
        # Telja verkefni
        fjoldi_i_vinnslu = Verkefni.objects.filter(stada='I_VINNSLU').count()
        fjoldi_lokid = Verkefni.objects.filter(
            stada='LOKID',
            lokad__date=dagur
        ).count()
        
        # Reikna tekjur og gjöld
        faerslur = Faersla.objects.filter(dagsetning=dagur)
        heildar_tekjur = faerslur.filter(tegund='TEKJUR').aggregate(
            heildar=Sum('fjarhaed')
        )['heildar'] or 0
        heildar_gjold = faerslur.filter(tegund='GJOLD').aggregate(
            heildar=Sum('fjarhaed')
        )['heildar'] or 0
        
        # Búa til eða uppfæra mælaborð
        maelabord, created = Maelabord.objects.update_or_create(
            notandi=request.user,
            dagsetning=dagur,
            defaults={
                'fjoldi_maettra': fjoldi_maettra,
                'fjoldi_verkefna_i_vinnslu': fjoldi_i_vinnslu,
                'fjoldi_verkefna_lokid': fjoldi_lokid,
                'heildar_tekjur': heildar_tekjur,
                'heildar_gjold': heildar_gjold,
            }
        )
        
        serializer = self.get_serializer(maelabord)
        return Response(serializer.data)
