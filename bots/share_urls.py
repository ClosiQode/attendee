from django.urls import path

from bots.share_views import (
    CreateSharedLinkView,
    DeleteSharedLinkView,
    ListSharedLinksView,
    SharedRecordingDownloadView,
    SharedRecordingPageView,
    SharedRecordingStreamView,
)

app_name = "share"

# API routes (authenticated)
api_urlpatterns = [
    path("bots/<str:object_id>/recording/share", CreateSharedLinkView.as_view(), name="create_shared_link"),
    path("bots/<str:object_id>/recording/shares", ListSharedLinksView.as_view(), name="list_shared_links"),
    path("bots/<str:object_id>/recording/shares/<str:token>", DeleteSharedLinkView.as_view(), name="delete_shared_link"),
]

# Public routes (no auth needed)
public_urlpatterns = [
    path("share/<str:token>/", SharedRecordingPageView.as_view(), name="shared_recording_page"),
    path("share/<str:token>/stream/", SharedRecordingStreamView.as_view(), name="shared_recording_stream"),
    path("share/<str:token>/download/", SharedRecordingDownloadView.as_view(), name="shared_recording_download"),
]
