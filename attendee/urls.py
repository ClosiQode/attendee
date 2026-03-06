"""
URL configuration for attendee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import json
import os

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from accounts import views
from bots.share_urls import api_urlpatterns as share_api_urlpatterns, public_urlpatterns as share_public_urlpatterns


def health_check_view(request):
    return HttpResponse(status=200)


def version_view(request):
    version_path = os.path.join(settings.BASE_DIR, "version.json")
    with open(version_path, "r", encoding="utf-8") as version_file:
        version_data = json.load(version_file)
    cuber_release = os.getenv("CUBER_RELEASE_VERSION")
    response_data = {"version": version_data.get("version")}
    if cuber_release:
        response_data["cuber_release"] = cuber_release
    return JsonResponse(
        response_data,
        status=200,
    )


urlpatterns = [
    path("health/", health_check_view, name="health-check"),
    path("version/", version_view, name="api-version"),
]

if not os.environ.get("DISABLE_ADMIN"):
    urlpatterns.append(path("admin/", admin.site.urls))

urlpatterns += [
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    path("external_webhooks/", include("bots.external_webhooks_urls", namespace="external_webhooks")),
    path("bot_sso/", include("bots.bot_sso_urls", namespace="bot_sso")),
    path("", views.home, name="home"),
    path("projects/", include("bots.projects_urls", namespace="projects")),
    path("api/v1/", include("bots.calendars_api_urls")),
    path("api/v1/", include("bots.zoom_oauth_connections_api_urls")),
    path("api/v1/", include("bots.app_session_api_urls")),
    path("api/v1/", include("bots.bots_api_urls")),
    path("api/v1/", include((share_api_urlpatterns, "share"))),
]

urlpatterns += share_public_urlpatterns

if settings.DEBUG:
    # API docs routes - only available in development
    urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]

# Serve local recording files when using local storage
if settings.STORAGE_PROTOCOL == "local":
    from django.views.static import serve as static_serve

    def serve_local_recording(request, path):
        from django.http import Http404

        # Only authenticated users can access recordings
        if not request.user.is_authenticated:
            raise Http404
        return static_serve(request, path, document_root=settings.LOCAL_RECORDING_STORAGE_PATH)

    def serve_local_audio_chunk(request, path):
        from django.http import Http404

        if not request.user.is_authenticated:
            raise Http404
        return static_serve(request, path, document_root=settings.LOCAL_AUDIO_CHUNK_STORAGE_PATH)

    urlpatterns += [
        re_path(r"^recordings/(?P<path>.*)$", serve_local_recording, name="local-recording"),
        re_path(r"^audio_chunks/(?P<path>.*)$", serve_local_audio_chunk, name="local-audio-chunk"),
    ]
