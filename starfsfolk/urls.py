from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotandiViewSet, StarfsmadurViewSet, MaetingViewSet,
    FridagurViewSet, VinnukostnadurViewSet, SerhaefiViewSet,
    TimaklukkuTaekiViewSet, TimaklukkuLeidrettingViewSet
)

router = DefaultRouter()
router.register(r'notendur', NotandiViewSet, basename='notandi')
router.register(r'starfsmenn', StarfsmadurViewSet, basename='starfsmadur')
router.register(r'maetingar', MaetingViewSet, basename='maeting')
router.register(r'timaklukku-taeki', TimaklukkuTaekiViewSet, basename='timaklukku-taeki')
router.register(r'timaklukku-leidrettingar', TimaklukkuLeidrettingViewSet, basename='timaklukku-leidretting')
router.register(r'fridagar', FridagurViewSet, basename='fridagur')
router.register(r'vinnukostnadur', VinnukostnadurViewSet, basename='vinnukostnadur')
router.register(r'serhaefi', SerhaefiViewSet, basename='serhaefi')

urlpatterns = [
    path('', include(router.urls)),
]
