from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from .models import FasturLidur, Reikningur, ReikningsLidur, Greidsla
from .serializers import (
    FasturLidurSerializer, ReikningurSerializer, ReikningurListSerializer,
    ReikningsLidurSerializer, GreidslaSerializer
)
from starfsfolk.permissions import IsSubAdminOrSuperAdmin


class FasturLidurViewSet(viewsets.ModelViewSet):
    queryset = FasturLidur.objects.all()
    serializer_class = FasturLidurSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def virkir(self, request):
        """Fá virka fasta liði"""
        virkir = self.queryset.filter(er_virkur=True)
        serializer = self.get_serializer(virkir, many=True)
        return Response(serializer.data)


class ReikningurViewSet(viewsets.ModelViewSet):
    queryset = Reikningur.objects.select_related(
        'vidskiptavinur', 'verkefni', 'stofnad_af'
    ).prefetch_related('lidur', 'greidslur')
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReikningurListSerializer
        return ReikningurSerializer
    
    def perform_create(self, serializer):
        serializer.save(stofnad_af=self.request.user)
    
    @action(detail=True, methods=['post'])
    def senda(self, request, pk=None):
        """Senda reikning til viðskiptavinar"""
        reikningur = self.get_object()
        reikningur.stada = 'SENDUR'
        reikningur.save()
        
        # Hérna væri hægt að senda tölvupóst
        
        serializer = self.get_serializer(reikningur)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def merkja_greiddan(self, request, pk=None):
        """Merkja reikning sem greiddan"""
        reikningur = self.get_object()
        reikningur.er_greiddur = True
        reikningur.stada = 'GREIDDUR'
        reikningur.save()
        
        serializer = self.get_serializer(reikningur)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def utistandandi(self, request):
        """Fá útistandandi reikninga"""
        utistandandi = self.queryset.filter(er_greiddur=False)
        serializer = ReikningurListSerializer(utistandandi, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def gjaldfallin(self, request):
        """Fá gjaldfallin reikninga"""
        dagur = timezone.now().date()
        gjaldfallin = self.queryset.filter(
            er_greiddur=False,
            gjalddagi__lt=dagur
        )
        serializer = ReikningurListSerializer(gjaldfallin, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sjalfvirkir_reikningar(self, request):
        """Búa til sjálfvirka reikninga síðasta dag mánaðar"""
        # Þetta myndi keyra með Celery task
        dagur = timezone.now().date()
        
        # Finna öll verkefni sem þarf að reikningsfæra
        from verkefni.models import Verkefni
        verkefni = Verkefni.objects.filter(
            stada='LOKID',
            reikningar__isnull=True
        )
        
        reikningar_stofnadir = []
        for verk in verkefni:
            if verk.verkbeidni and verk.verkbeidni.vidskiptavinur:
                reikningur = Reikningur.objects.create(
                    vidskiptavinur=verk.verkbeidni.vidskiptavinur,
                    verkefni=verk,
                    reikningsdagsetning=dagur,
                    gjalddagi=dagur + timedelta(days=30),
                    eindagi=dagur + timedelta(days=45),
                    stofnad_af=request.user
                )
                reikningar_stofnadir.append(reikningur)
        
        serializer = ReikningurListSerializer(reikningar_stofnadir, many=True)
        return Response({
            'fjoldi': len(reikningar_stofnadir),
            'reikningar': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exporta reikninga sem PDF"""
        from bokhald.pdf_utils import generate_reikningur_pdf
        reikningar = self.queryset.all()
        return generate_reikningur_pdf(reikningar)


class ReikningsLidurViewSet(viewsets.ModelViewSet):
    queryset = ReikningsLidur.objects.select_related('reikningur')
    serializer_class = ReikningsLidurSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]


class GreidslaViewSet(viewsets.ModelViewSet):
    queryset = Greidsla.objects.select_related('reikningur', 'skrad_af')
    serializer_class = GreidslaSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    def perform_create(self, serializer):
        serializer.save(skrad_af=self.request.user)
