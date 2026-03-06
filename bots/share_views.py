import logging

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from bots.authentication import ApiKeyAuthentication
from bots.models import Bot, Recording, SharedRecordingAccess, SharedRecordingLink
from bots.storage import remote_storage_url

logger = logging.getLogger(__name__)


class CreateSharedLinkView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def post(self, request, object_id):
        bot = get_object_or_404(Bot, object_id=object_id, project=request.auth.project)
        recording = Recording.objects.filter(bot=bot, is_default_recording=True).first()
        if not recording or not recording.file or not recording.file.name:
            return Response({"error": "No recording found for this bot"}, status=status.HTTP_404_NOT_FOUND)

        expires_in_hours = request.data.get("expires_in_hours")
        allow_download = request.data.get("allow_download", True)
        title = request.data.get("title", "")

        expires_at = None
        if expires_in_hours is not None:
            expires_at = timezone.now() + timezone.timedelta(hours=int(expires_in_hours))

        shared_link = SharedRecordingLink.objects.create(
            recording=recording,
            created_by=request.user if request.user.is_authenticated else None,
            expires_at=expires_at,
            allow_download=allow_download,
            title=title,
        )

        return Response({
            "token": shared_link.token,
            "share_url": request.build_absolute_uri(f"/share/{shared_link.token}/"),
            "expires_at": shared_link.expires_at,
            "allow_download": shared_link.allow_download,
        }, status=status.HTTP_201_CREATED)


class ListSharedLinksView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def get(self, request, object_id):
        bot = get_object_or_404(Bot, object_id=object_id, project=request.auth.project)
        recording = Recording.objects.filter(bot=bot, is_default_recording=True).first()
        if not recording:
            return Response({"error": "No recording found"}, status=status.HTTP_404_NOT_FOUND)

        links = SharedRecordingLink.objects.filter(recording=recording).order_by("-created_at")
        data = []
        for link in links:
            data.append({
                "token": link.token,
                "share_url": request.build_absolute_uri(f"/share/{link.token}/"),
                "created_at": link.created_at,
                "expires_at": link.expires_at,
                "is_active": link.is_active,
                "is_valid": link.is_valid,
                "access_count": link.access_count,
                "allow_download": link.allow_download,
            })
        return Response(data)


class DeleteSharedLinkView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def delete(self, request, object_id, token):
        bot = get_object_or_404(Bot, object_id=object_id, project=request.auth.project)
        recording = Recording.objects.filter(bot=bot, is_default_recording=True).first()
        if not recording:
            return Response({"error": "No recording found"}, status=status.HTTP_404_NOT_FOUND)

        shared_link = get_object_or_404(SharedRecordingLink, recording=recording, token=token)
        shared_link.is_active = False
        shared_link.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SharedRecordingPageView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        shared_link = SharedRecordingLink.objects.filter(token=token).first()

        if not shared_link or not shared_link.is_valid:
            return render(request, "shared_recording_expired.html", status=404)

        recording = shared_link.recording

        # Track access
        SharedRecordingAccess.objects.create(
            shared_link=shared_link,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        shared_link.access_count = shared_link.access_count + 1
        shared_link.save(update_fields=["access_count"])

        # Get video URL based on storage protocol
        video_url = self._get_video_url(recording, request)

        context = {
            "recording": recording,
            "shared_link": shared_link,
            "video_url": video_url,
            "bot": recording.bot,
        }
        return render(request, "shared_recording.html", context)

    def _get_video_url(self, recording, request):
        if settings.STORAGE_PROTOCOL == "local":
            return request.build_absolute_uri(f"/share/{recording.shared_links.filter(is_active=True).first().token}/stream/")
        return recording.url

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class SharedRecordingStreamView(APIView):
    """Serve video file directly for local storage mode."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        shared_link = get_object_or_404(SharedRecordingLink, token=token)

        if not shared_link.is_valid:
            raise Http404("This shared link has expired or been deactivated.")

        recording = shared_link.recording
        if not recording.file or not recording.file.name:
            raise Http404("Recording file not found.")

        file_path = recording.file.path
        response = FileResponse(open(file_path, "rb"), content_type="video/mp4")
        response["Content-Disposition"] = f'inline; filename="{recording.file.name.split("/")[-1]}"'
        return response


class SharedRecordingDownloadView(APIView):
    """Download the recording file."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, token):
        shared_link = get_object_or_404(SharedRecordingLink, token=token)

        if not shared_link.is_valid:
            raise Http404("This shared link has expired or been deactivated.")

        if not shared_link.allow_download:
            return Response({"error": "Download is not allowed for this shared link"}, status=status.HTTP_403_FORBIDDEN)

        recording = shared_link.recording
        if not recording.file or not recording.file.name:
            raise Http404("Recording file not found.")

        if settings.STORAGE_PROTOCOL == "local":
            file_path = recording.file.path
            response = FileResponse(open(file_path, "rb"), content_type="video/mp4")
            response["Content-Disposition"] = f'attachment; filename="{recording.file.name.split("/")[-1]}"'
            return response
        else:
            # Redirect to presigned URL for cloud storage
            from django.shortcuts import redirect
            return redirect(recording.url)
