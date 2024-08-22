from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from debug_toolbar.toolbar import debug_toolbar_urls

import zipprocessor.urls
import user.urls

urlpatterns = [
    path('', include(zipprocessor.urls)),
    path('admin/', admin.site.urls),
    path("user/", include(user.urls)),
    path("user/", include("django.contrib.auth.urls")),
] + debug_toolbar_urls() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
