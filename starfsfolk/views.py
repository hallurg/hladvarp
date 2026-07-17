from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import (
    Notandi, Starfsmadur, Maeting, Fridagur,
    Vinnukostnadur, Serhaefi, TimaklukkuTaeki,
    TimaklukkuAtburdur, TimaklukkuLeidretting
)
from .serializers import (
    NotandiSerializer, StarfsmadurSerializer, StarfsmadurCreateSerializer,
    MaetingSerializer, FridagurSerializer, VinnukostnadurSerializer,
    SerhaefiSerializer, TimaklukkuTaekiSerializer,
    TimaklukkuAtburdurSerializer, TimaklukkuLeidrettingSerializer
)
from .permissions import IsSubAdminOrSuperAdmin


def get_current_starfsmadur(user):
    try:
        return user.starfsmadur_profile
    except Starfsmadur.DoesNotExist:
        return None


def is_manager(user):
    return (
        user
        and user.is_authenticated
        and user.notendategund in ['SUB_ADMIN', 'SUPER_ADMIN']
    )


class NotandiViewSet(viewsets.ModelViewSet):
    queryset = Notandi.objects.all()
    serializer_class = NotandiSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]

    @action(detail=False, methods=['get'])
    def minn_profill(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class StarfsmadurViewSet(viewsets.ModelViewSet):
    queryset = Starfsmadur.objects.select_related('notandi').prefetch_related('serhaefi').order_by('rodun', '-stofnad')
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return StarfsmadurCreateSerializer
        return StarfsmadurSerializer

    @action(detail=True, methods=['post'])
    def loka_adgangi(self, request, pk=None):
        starfsmadur = self.get_object()
        starfsmadur.er_virkur = False
        starfsmadur.notandi.er_virkur = False
        starfsmadur.save()
        starfsmadur.notandi.save()

        return Response({
            'status': 'Adgangi lokad',
            'starfsmadur': StarfsmadurSerializer(starfsmadur).data
        })

    @action(detail=False, methods=['get'])
    def virkir(self, request):
        starfsmenn = self.queryset.filter(er_virkur=True)
        serializer = self.get_serializer(starfsmenn, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        from bokhald.pdf_utils import generate_starfsmann_pdf
        starfsmenn = self.queryset.filter(er_virkur=True)
        return generate_starfsmann_pdf(starfsmenn)


class MaetingViewSet(viewsets.ModelViewSet):
    queryset = Maeting.objects.select_related('starfsmadur__notandi')
    serializer_class = MaetingSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def stimplast_inn(self, request):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        maeting, created = Maeting.objects.get_or_create(
            starfsmadur=starfsmadur,
            dagsetning=now.date(),
            defaults={
                'moettartimi': now,
                'status': 'MAETTUR'
            }
        )

        if not created:
            maeting.moettartimi = now
            maeting.status = 'MAETTUR'
            maeting.save()

        taeki = self._get_request_device(request, starfsmadur)
        TimaklukkuAtburdur.objects.create(
            starfsmadur=starfsmadur,
            taeki=taeki,
            event_type='IN',
            source='PHONE' if taeki else 'API',
            note=request.data.get('note', ''),
            created_by=request.user,
        )

        serializer = self.get_serializer(maeting)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def stimplast_ut(self, request):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dagur = timezone.now().date()
        try:
            maeting = Maeting.objects.get(
                starfsmadur=starfsmadur,
                dagsetning=dagur
            )
            maeting.brottfararstimi = timezone.now()
            maeting.save()

            taeki = self._get_request_device(request, starfsmadur)
            TimaklukkuAtburdur.objects.create(
                starfsmadur=starfsmadur,
                taeki=taeki,
                event_type='OUT',
                source='PHONE' if taeki else 'API',
                note=request.data.get('note', ''),
                created_by=request.user,
            )

            serializer = self.get_serializer(maeting)
            return Response(serializer.data)
        except Maeting.DoesNotExist:
            return Response(
                {'villa': 'Engin maeting skrad fyrir daginn'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def mobile_ingest(self, request):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        client_event_id = request.data.get('client_event_id')
        if not client_event_id:
            return Response(
                {'villa': 'client_event_id er skylda fyrir idempotent mobile ingest'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_type = request.data.get('event_type')
        if event_type not in ['IN', 'OUT']:
            return Response(
                {'villa': 'event_type verdur ad vera IN eda OUT'},
                status=status.HTTP_400_BAD_REQUEST
            )

        taeki = self._get_request_device(request, starfsmadur)
        if taeki is None:
            return Response(
                {'villa': 'Virkt tengt taeki er skylda fyrir mobile ingest'},
                status=status.HTTP_400_BAD_REQUEST
            )

        source = request.data.get('source', 'MOBILE')
        if source not in ['MOBILE', 'BIXBY', 'PHONE']:
            source = 'MOBILE'

        event_timestamp = self._parse_client_timestamp(request.data.get('timestamp'))
        safe_payload = {
            'event_type': event_type,
            'client_event_id': client_event_id,
            'timestamp': request.data.get('timestamp', ''),
            'source': source,
            'note': request.data.get('note', ''),
            'taeki': taeki.id,
        }

        with transaction.atomic():
            existing_event = TimaklukkuAtburdur.objects.select_for_update().filter(
                client_event_id=client_event_id
            ).first()
            if existing_event:
                maeting = self._maeting_for_event(existing_event)
                return Response({
                    'idempotent_replay': True,
                    'event': TimaklukkuAtburdurSerializer(existing_event).data,
                    'maeting': MaetingSerializer(maeting).data if maeting else None,
                })

            maeting = self._apply_clock_event(starfsmadur, event_type, event_timestamp)
            event = TimaklukkuAtburdur.objects.create(
                starfsmadur=starfsmadur,
                taeki=taeki,
                event_type=event_type,
                timestamp=event_timestamp,
                source=source,
                client_event_id=client_event_id,
                raw_payload=safe_payload,
                note=request.data.get('note', ''),
                created_by=request.user,
            )
            taeki.last_seen = timezone.now()
            taeki.save(update_fields=['last_seen'])

        return Response({
            'idempotent_replay': False,
            'event': TimaklukkuAtburdurSerializer(event).data,
            'maeting': MaetingSerializer(maeting).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def maetiyfirlit_dagsins(self, request):
        dagur = timezone.now().date()
        maetingar = self.queryset.filter(dagsetning=dagur)
        serializer = self.get_serializer(maetingar, many=True)

        stats = {
            'maettir': maetingar.filter(status='MAETTUR').count(),
            'fjarverandi': maetingar.filter(status='FJARVERANDI').count(),
            'veikir': maetingar.filter(status='VEIKUR').count(),
            'fri': maetingar.filter(status='FRI').count(),
            'utkoll': maetingar.filter(status='UTKALL').count(),
        }

        return Response({
            'dagsetning': dagur,
            'tolur': stats,
            'maetingar': serializer.data
        })

    @action(detail=False, methods=['get'])
    def current_status(self, request):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        dagur = timezone.now().date()
        maeting = self.queryset.filter(starfsmadur=starfsmadur, dagsetning=dagur).first()
        latest_event = TimaklukkuAtburdur.objects.filter(starfsmadur=starfsmadur).first()
        active_device_count = TimaklukkuTaeki.objects.filter(
            starfsmadur=starfsmadur,
            status='ACTIVE'
        ).count()

        is_clocked_in = bool(maeting and maeting.moettartimi and not maeting.brottfararstimi)
        return Response({
            'starfsmadur': starfsmadur.id,
            'starfsmadur_nafn': starfsmadur.notandi.fullt_nafn,
            'dagsetning': dagur,
            'is_clocked_in': is_clocked_in,
            'maeting': MaetingSerializer(maeting).data if maeting else None,
            'latest_event': TimaklukkuAtburdurSerializer(latest_event).data if latest_event else None,
            'active_device_count': active_device_count,
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        events = TimaklukkuAtburdur.objects.filter(starfsmadur=starfsmadur)[:50]
        return Response(TimaklukkuAtburdurSerializer(events, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsSubAdminOrSuperAdmin])
    def manager_summary(self, request):
        dagur = timezone.now().date()
        maetingar = self.queryset.filter(dagsetning=dagur)
        corrections = TimaklukkuLeidretting.objects.all()
        return Response({
            'dagsetning': dagur,
            'maettir': maetingar.filter(status='MAETTUR').count(),
            'i_vinnu_nuna': maetingar.filter(
                moettartimi__isnull=False,
                brottfararstimi__isnull=True
            ).count(),
            'utstimpladir': maetingar.filter(brottfararstimi__isnull=False).count(),
            'bidur_samthykkis': corrections.filter(status='PENDING').count(),
            'active_devices': TimaklukkuTaeki.objects.filter(status='ACTIVE').count(),
            'latest_events': TimaklukkuAtburdurSerializer(
                TimaklukkuAtburdur.objects.all()[:10],
                many=True
            ).data,
        })

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        from bokhald.pdf_utils import generate_maeting_pdf
        fra_dags = request.query_params.get('fra_dagsetning')
        til_dags = request.query_params.get('til_dagsetning')

        queryset = self.queryset
        if fra_dags:
            queryset = queryset.filter(dagsetning__gte=fra_dags)
        if til_dags:
            queryset = queryset.filter(dagsetning__lte=til_dags)

        maetingar = queryset.order_by('-dagsetning')
        return generate_maeting_pdf(maetingar)

    def _get_request_device(self, request, starfsmadur):
        taeki_id = request.data.get('taeki') or request.data.get('taeki_id')
        if not taeki_id:
            return None
        return TimaklukkuTaeki.objects.filter(
            id=taeki_id,
            starfsmadur=starfsmadur,
            status='ACTIVE'
        ).first()

    def _parse_client_timestamp(self, value):
        if not value:
            return timezone.now()
        parsed = parse_datetime(value)
        if parsed is None:
            return timezone.now()
        if timezone.is_naive(parsed):
            return timezone.make_aware(parsed, timezone.get_current_timezone())
        return parsed

    def _maeting_for_event(self, event):
        return self.queryset.filter(
            starfsmadur=event.starfsmadur,
            dagsetning=event.timestamp.date()
        ).first()

    def _apply_clock_event(self, starfsmadur, event_type, event_timestamp):
        maeting, _ = Maeting.objects.get_or_create(
            starfsmadur=starfsmadur,
            dagsetning=event_timestamp.date(),
            defaults={'status': 'FJARVERANDI'}
        )
        if event_type == 'IN':
            maeting.moettartimi = event_timestamp
            maeting.status = 'MAETTUR'
        if event_type == 'OUT':
            maeting.brottfararstimi = event_timestamp
        maeting.save()
        return maeting


class TimaklukkuTaekiViewSet(viewsets.ModelViewSet):
    queryset = TimaklukkuTaeki.objects.select_related('starfsmadur__notandi')
    serializer_class = TimaklukkuTaekiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if is_manager(self.request.user):
            return queryset
        starfsmadur = get_current_starfsmadur(self.request.user)
        if starfsmadur is None:
            return queryset.none()
        return queryset.filter(starfsmadur=starfsmadur)

    def create(self, request, *args, **kwargs):
        starfsmadur = get_current_starfsmadur(request.user)
        if starfsmadur is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pairing_code = TimaklukkuTaeki.generate_pairing_code()
        taeki = TimaklukkuTaeki(
            starfsmadur=starfsmadur,
            device_label=serializer.validated_data.get('device_label', '')
        )
        taeki.set_pairing_code(pairing_code)
        taeki.save()

        response_data = TimaklukkuTaekiSerializer(taeki).data
        response_data['pairing_code'] = pairing_code
        response_data['pairing_code_visible_once'] = True
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def mine(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        taeki = self.get_object()
        if taeki.status == 'REVOKED':
            return Response(
                {'villa': 'Taeki hefur verid afturkallad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if taeki.status == 'PAIRING' and not taeki.matches_pairing_code(request.data.get('pairing_code')):
            return Response(
                {'villa': 'Ogildur tengikodi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        taeki.activate()
        TimaklukkuAtburdur.objects.create(
            starfsmadur=taeki.starfsmadur,
            taeki=taeki,
            event_type='DEVICE_CONNECTED',
            source='PHONE',
            created_by=request.user,
        )
        return Response(self.get_serializer(taeki).data)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        taeki = self.get_object()
        taeki.revoke()
        TimaklukkuAtburdur.objects.create(
            starfsmadur=taeki.starfsmadur,
            taeki=taeki,
            event_type='DEVICE_REVOKED',
            source='ADMIN' if is_manager(request.user) else 'PHONE',
            created_by=request.user,
        )
        return Response(self.get_serializer(taeki).data)


class TimaklukkuLeidrettingViewSet(viewsets.ModelViewSet):
    queryset = TimaklukkuLeidretting.objects.select_related(
        'starfsmadur__notandi',
        'maeting',
        'reviewed_by',
    )
    serializer_class = TimaklukkuLeidrettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if is_manager(self.request.user):
            return queryset
        starfsmadur = get_current_starfsmadur(self.request.user)
        if starfsmadur is None:
            return queryset.none()
        return queryset.filter(starfsmadur=starfsmadur)

    def create(self, request, *args, **kwargs):
        if get_current_starfsmadur(request.user) is None:
            return Response(
                {'villa': 'Notandi er ekki skradur sem starfsmadur'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        starfsmadur = get_current_starfsmadur(self.request.user)
        correction = serializer.save(starfsmadur=starfsmadur)
        TimaklukkuAtburdur.objects.create(
            starfsmadur=correction.starfsmadur,
            event_type='CORRECTION_REQUESTED',
            source='PHONE',
            note=correction.requested_change,
            created_by=self.request.user,
        )

    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def approve(self, request, pk=None):
        correction = self.get_object()
        correction.approve(request.user, request.data.get('manager_note', ''))
        TimaklukkuAtburdur.objects.create(
            starfsmadur=correction.starfsmadur,
            event_type='CORRECTION_APPROVED',
            source='ADMIN',
            note=correction.manager_note,
            created_by=request.user,
        )
        return Response(self.get_serializer(correction).data)

    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def reject(self, request, pk=None):
        correction = self.get_object()
        correction.reject(request.user, request.data.get('manager_note', ''))
        TimaklukkuAtburdur.objects.create(
            starfsmadur=correction.starfsmadur,
            event_type='CORRECTION_REJECTED',
            source='ADMIN',
            note=correction.manager_note,
            created_by=request.user,
        )
        return Response(self.get_serializer(correction).data)


class FridagurViewSet(viewsets.ModelViewSet):
    queryset = Fridagur.objects.select_related('starfsmadur__notandi', 'samthykkt_af')
    serializer_class = FridagurSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'starfsmadur_profile'):
            serializer.save(starfsmadur=self.request.user.starfsmadur_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def samthykkja(self, request, pk=None):
        fridagur = self.get_object()
        fridagur.stada = 'SAMTHYKKTUR'
        fridagur.samthykkt_af = request.user
        fridagur.save()

        serializer = self.get_serializer(fridagur)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def synja(self, request, pk=None):
        fridagur = self.get_object()
        fridagur.stada = 'SYNJAD'
        fridagur.samthykkt_af = request.user
        fridagur.save()

        serializer = self.get_serializer(fridagur)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsSubAdminOrSuperAdmin])
    def obidnar_beidnir(self, request):
        beidnir = self.queryset.filter(stada='OBIDINN')
        serializer = self.get_serializer(beidnir, many=True)
        return Response(serializer.data)


class VinnukostnadurViewSet(viewsets.ModelViewSet):
    queryset = Vinnukostnadur.objects.select_related('starfsmadur__notandi')
    serializer_class = VinnukostnadurSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def samantekt(self, request):
        starfsmadur_id = request.query_params.get('starfsmadur')
        fra_dags = request.query_params.get('fra_dagsetning')
        til_dags = request.query_params.get('til_dagsetning')

        queryset = self.queryset

        if starfsmadur_id:
            queryset = queryset.filter(starfsmadur_id=starfsmadur_id)
        if fra_dags:
            queryset = queryset.filter(dagsetning__gte=fra_dags)
        if til_dags:
            queryset = queryset.filter(dagsetning__lte=til_dags)

        heildar_kostnadur = sum(k.fjarhaed for k in queryset)
        greiddur_kostnadur = sum(k.fjarhaed for k in queryset.filter(er_greitt=True))
        ogreiddur_kostnadur = sum(k.fjarhaed for k in queryset.filter(er_greitt=False))

        return Response({
            'heildar_kostnadur': heildar_kostnadur,
            'greiddur_kostnadur': greiddur_kostnadur,
            'ogreiddur_kostnadur': ogreiddur_kostnadur,
            'fjoldi_faerslna': queryset.count()
        })


class SerhaefiViewSet(viewsets.ModelViewSet):
    queryset = Serhaefi.objects.all()
    serializer_class = SerhaefiSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
