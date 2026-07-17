from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VerkbeidniViewSet, VerkefniViewSet, VerkefniSkraViewSet,
    VerkefniAthugasemdViewSet, DeadlineAminnningViewSet
)

router = DefaultRouter()
router.register(r'verkbeidnir', VerkbeidniViewSet, basename='verkbeidni')
router.register(r'', VerkefniViewSet, basename='verkefni')
router.register(r'skrar', VerkefniSkraViewSet, basename='verkefniskra')
router.register(r'athugasemdir', VerkefniAthugasemdViewSet, basename='athugasemd')
router.register(r'aminningar', DeadlineAminnningViewSet, basename='aminnning')

urlpatterns = [
    path('', include(router.urls)),
]
