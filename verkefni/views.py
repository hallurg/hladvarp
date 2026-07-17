from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (
    Verkbeiðni, Verkefni, VerkefniSkra,
    VerkefniAthugasemd, DeadlineAminnning
)
from .serializers import (
    VerkbeidniSerializer, VerkefniSerializer, VerkefniListSerializer,
    VerkefniSkraSerializer, VerkefniAthugasemdSerializer,
    DeadlineAminnningSerializer
)
from starfsfolk.permissions import IsSubAdminOrSuperAdmin


class VerkbeidniViewSet(viewsets.ModelViewSet):
    queryset = Verkbeiðni.objects.select_related('vidskiptavinur', 'stofnad_af', 'samthykkt_af')
    serializer_class = VerkbeidniSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(stofnad_af=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def samthykkja(self, request, pk=None):
        """Yfirmaður samþykkir verkbeiðni"""
        verkbeidni = self.get_object()
        verkbeidni.stada = 'SAMTHYKKTUR'
        verkbeidni.samthykkt_af = request.user
        verkbeidni.save()
        
        serializer = self.get_serializer(verkbeidni)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsSubAdminOrSuperAdmin])
    def synja(self, request, pk=None):
        """Yfirmaður synja verkbeiðni"""
        verkbeidni = self.get_object()
        verkbeidni.stada = 'SYNJAD'
        verkbeidni.samthykkt_af = request.user
        verkbeidni.save()
        
        serializer = self.get_serializer(verkbeidni)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def obidnar(self, request):
        """Fá lista yfir óbíðnar verkbeiðnir"""
        obidnar = self.queryset.filter(stada='OBIDINN')
        serializer = self.get_serializer(obidnar, many=True)
        return Response(serializer.data)


class VerkefniViewSet(viewsets.ModelViewSet):
    queryset = Verkefni.objects.select_related(
        'verkbeidni', 'starfsmadur__notandi', 'uthlutad_af'
    ).prefetch_related('skrar', 'athugasemdir').order_by('rodun', '-stofnad')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VerkefniListSerializer
        return VerkefniSerializer
    
    def perform_create(self, serializer):
        serializer.save(uthlutad_af=self.request.user)
    
    @action(detail=True, methods=['post'])
    def byrja(self, request, pk=None):
        """Starfsmaður byrjar á verkefni"""
        verkefni = self.get_object()
        verkefni.stada = 'I_VINNSLU'
        verkefni.save()
        
        serializer = self.get_serializer(verkefni)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ljuka(self, request, pk=None):
        """Ljúka verkefni"""
        verkefni = self.get_object()
        verkefni.stada = 'LOKID'
        verkefni.lokad = timezone.now()
        verkefni.save()
        
        serializer = self.get_serializer(verkefni)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def min_verkefni(self, request):
        """Fá verkefni innskráðs starfsmanns"""
        try:
            starfsmadur = request.user.starfsmadur_profile
            verkefni = self.queryset.filter(starfsmadur=starfsmadur)
            serializer = VerkefniListSerializer(verkefni, many=True)
            return Response(serializer.data)
        except:
            return Response(
                {'villa': 'Notandi er ekki skráður sem starfsmaður'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def i_vinnslu(self, request):
        """Fá öll verkefni í vinnslu"""
        verkefni = self.queryset.filter(stada='I_VINNSLU')
        serializer = VerkefniListSerializer(verkefni, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def yfirlit(self, request):
        """Fá yfirlit yfir stöðu verkefna"""
        obidinn = self.queryset.filter(stada='OBIDINN').count()
        i_vinnslu = self.queryset.filter(stada='I_VINNSLU').count()
        lokid = self.queryset.filter(stada='LOKID').count()
        a_hold = self.queryset.filter(stada='A_HOLD').count()
        
        return Response({
            'obidinn': obidinn,
            'i_vinnslu': i_vinnslu,
            'lokid': lokid,
            'a_hold': a_hold,
            'samtals': self.queryset.count()
        })
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exporta verkefni sem PDF"""
        from bokhald.pdf_utils import generate_verkefni_pdf
        verkefni_list = self.queryset.all()
        return generate_verkefni_pdf(verkefni_list)


class VerkefniSkraViewSet(viewsets.ModelViewSet):
    queryset = VerkefniSkra.objects.select_related('verkefni', 'upphlad_af')
    serializer_class = VerkefniSkraSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(upphlad_af=self.request.user)


class VerkefniAthugasemdViewSet(viewsets.ModelViewSet):
    queryset = VerkefniAthugasemd.objects.select_related('verkefni', 'notandi')
    serializer_class = VerkefniAthugasemdSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(notandi=self.request.user)


class DeadlineAminnningViewSet(viewsets.ModelViewSet):
    queryset = DeadlineAminnning.objects.select_related('verkefni')
    serializer_class = DeadlineAminnningSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
