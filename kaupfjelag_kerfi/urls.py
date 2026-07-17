"""
URL configuration for kaupfjelag_kerfi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('starfsmannahald/demo/', views.timekeeping_demo, name='timekeeping_demo'),

    path('askrift/', include('askrift.urls')),

    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/starfsfolk/', include('starfsfolk.urls')),
    path('api/verkefni/', include('verkefni.urls')),
    path('api/vidskiptavinir/', include('vidskiptavinir.urls')),
    path('api/reikningar/', include('reikningar.urls')),
    path('api/bokhald/', include('bokhald.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
