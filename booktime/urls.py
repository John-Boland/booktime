from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main import admin

urlpatterns = [
    path('admin/', admin.main_admin.urls),
    path('office-admin/', admin.central_office_admin.urls),
    path('dispatch-admin/', admin.dispatchers_admin.urls),
    path('', include('main.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("", include("main.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
