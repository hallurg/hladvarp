from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VidskiptavinurViewSet, KerfisnumerViewSet

router = DefaultRouter()
router.register(r'', VidskiptavinurViewSet, basename='vidskiptavinur')
router.register(r'kerfisnumer', KerfisnumerViewSet, basename='kerfisnumer')

urlpatterns = [
    path('', include(router.urls)),
]
