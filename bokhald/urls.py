from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FaerslaViewSet, SuperAdminKerfiskaukandiViewSet, MaelabordViewSet,
    BokhaldslykillViewSet
)

router = DefaultRouter()
router.register(r'bokhaldslyklar', BokhaldslykillViewSet, basename='bokhaldslykill')
router.register(r'faerslur', FaerslaViewSet, basename='faersla')
router.register(r'kerfiskaupendur', SuperAdminKerfiskaukandiViewSet, basename='kerfiskaupandi')
router.register(r'maelabord', MaelabordViewSet, basename='maelabord')

urlpatterns = [
    path('', include(router.urls)),
]
