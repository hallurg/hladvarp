from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FasturLidurViewSet, ReikningurViewSet,
    ReikningsLidurViewSet, GreidslaViewSet
)

router = DefaultRouter()
router.register(r'fastir-lidir', FasturLidurViewSet, basename='fastur-lidur')
router.register(r'', ReikningurViewSet, basename='reikningur')
router.register(r'lidir', ReikningsLidurViewSet, basename='reikningslidur')
router.register(r'greidslur', GreidslaViewSet, basename='greidsla')

urlpatterns = [
    path('', include(router.urls)),
]
