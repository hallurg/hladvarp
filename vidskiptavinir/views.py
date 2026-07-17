from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vidskiptavinur, Kerfisnumer
from .serializers import (
    VidskiptavinurSerializer, VidskiptavinurListSerializer,
    KerfisnumerSerializer
)
from starfsfolk.permissions import IsSubAdminOrSuperAdmin


class VidskiptavinurViewSet(viewsets.ModelViewSet):
    queryset = Vidskiptavinur.objects.prefetch_related('kerfisnumer')
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VidskiptavinurListSerializer
        return VidskiptavinurSerializer
    
    @action(detail=True, methods=['get'])
    def fjarhagur(self, request, pk=None):
        """Fá ítarlegar fjárhagsupplýsingar viðskiptavinar"""
        vidskiptavinur = self.get_object()
        
        from reikningar.models import Reikningur, Greidsla
        
        reikningar = Reikningur.objects.filter(vidskiptavinur=vidskiptavinur)
        greidslur = Greidsla.objects.filter(reikningur__vidskiptavinur=vidskiptavinur)
        
        heildar_reikningar = sum(r.heildarfjarhaed for r in reikningar)
        heildar_greidslur = sum(g.fjarhaed for g in greidslur)
        
        return Response({
            'vidskiptavinur': VidskiptavinurSerializer(vidskiptavinur).data,
            'fjoldi_reikninga': reikningar.count(),
            'heildar_reikningar': heildar_reikningar,
            'heildar_greidslur': heildar_greidslur,
            'skuldastada': vidskiptavinur.skuldastada,
            'utistandandi_reikningar': reikningar.filter(er_greiddur=False).count()
        })
    
    @action(detail=False, methods=['get'])
    def skuldarar(self, request):
        """Fá lista yfir viðskiptavini með skuldir"""
        skuldarar = self.queryset.filter(skuldastada__gt=0)
        serializer = VidskiptavinurListSerializer(skuldarar, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Exporta viðskiptavini sem PDF"""
        from bokhald.pdf_utils import generate_vidskiptavin_pdf
        vidskiptavinir = self.queryset.all()
        return generate_vidskiptavin_pdf(vidskiptavinir)


class KerfisnumerViewSet(viewsets.ModelViewSet):
    queryset = Kerfisnumer.objects.select_related('vidskiptavinur')
    serializer_class = KerfisnumerSerializer
    permission_classes = [IsAuthenticated, IsSubAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def eftir_vidskiptavin(self, request):
        """Fá kerfisnúmer fyrir tiltekinn viðskiptavin"""
        vidskiptavinur_id = request.query_params.get('vidskiptavinur')
        if not vidskiptavinur_id:
            return Response(
                {'villa': 'Vantar viðskiptavinur parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        kerfisnumer = self.queryset.filter(
            vidskiptavinur_id=vidskiptavinur_id,
            er_virkur=True
        )
        serializer = self.get_serializer(kerfisnumer, many=True)
        return Response(serializer.data)
