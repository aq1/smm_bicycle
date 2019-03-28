from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import (
    static,
    staticfiles_urlpatterns,
)


urlpatterns = [
    path('a/', admin.site.urls),
    path('', include('smm_admin.urls')),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
