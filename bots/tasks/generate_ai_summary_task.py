import logging

from celery import shared_task

from bots.ai_summary_providers import generate_summary
from bots.models import Credentials, Recording

logger = logging.getLogger(__name__)


@shared_task(bind=True, soft_time_limit=300, max_retries=2)
def generate_ai_summary_task(self, recording_id):
    """
    Génère une synthèse IA pour un enregistrement après la transcription.
    """
    try:
        recording = Recording.objects.select_related("bot__project__ai_summary_settings").get(id=recording_id)
    except Recording.DoesNotExist:
        logger.error(f"Recording {recording_id} not found")
        raise

    ai_summary_settings = recording.bot.project.ai_summary_settings

    # Si la synthèse IA n'est pas activée, ne rien faire
    if not ai_summary_settings.enabled:
        logger.info(f"AI summary is disabled for project {recording.bot.project.object_id}")
        return

    # Mettre ai_summary_status en IN_PROGRESS
    recording.ai_summary_status = Recording.AISummaryStatus.IN_PROGRESS
    recording.save(update_fields=["ai_summary_status"])

    try:
        # Récupérer le texte de transcription complet à partir de toutes les utterances
        utterances = recording.utterances.filter(
            transcription__isnull=False,
            failure_data__isnull=True
        ).order_by("timestamp_ms")

        transcription_text = "\n".join(
            utterance.transcription.get("transcript", "")
            for utterance in utterances
        )

        # Si pas de transcription, marquer comme FAILED
        if not transcription_text.strip():
            recording.ai_summary_status = Recording.AISummaryStatus.FAILED
            recording.ai_summary_failure_data = {"error": "No transcription found"}
            recording.save(update_fields=["ai_summary_status", "ai_summary_failure_data"])
            return

        # Mapper le provider vers le credential_type
        provider_to_credential_type = {
            1: Credentials.CredentialTypes.OPENAI,  # OpenAI
            2: Credentials.CredentialTypes.ANTHROPIC,  # Anthropic
            3: Credentials.CredentialTypes.MISTRAL,  # Mistral
        }
        credential_type = provider_to_credential_type.get(ai_summary_settings.provider)

        # Récupérer les credentials et les déchiffrer
        credentials_record = recording.bot.project.credentials.filter(
            credential_type=credential_type
        ).first()

        if not credentials_record:
            raise ValueError(f"No credentials found for provider {ai_summary_settings.provider}")

        credentials = credentials_record.get_credentials()
        if not credentials:
            raise ValueError("Failed to decrypt credentials")

        # Générer la synthèse
        api_key = credentials.get("api_key")
        if not api_key:
            raise ValueError("API key not found in credentials")

        summary = generate_summary(
            provider=ai_summary_settings.provider,
            api_key=api_key,
            model_name=ai_summary_settings.model_name or "",
            system_prompt=ai_summary_settings.system_prompt,
            transcription_text=transcription_text,
            reasoning_effort=ai_summary_settings.reasoning_effort or "low",
        )

        # Stocker le résultat
        recording.ai_summary = summary
        recording.ai_summary_status = Recording.AISummaryStatus.COMPLETE
        recording.save(update_fields=["ai_summary", "ai_summary_status"])

        logger.info(f"AI summary generated successfully for recording {recording_id}")

    except Exception as e:
        logger.error(f"Error generating AI summary for recording {recording_id}: {str(e)}")
        recording.ai_summary_status = Recording.AISummaryStatus.FAILED
        recording.ai_summary_failure_data = {"error": str(e)}
        recording.save(update_fields=["ai_summary_status", "ai_summary_failure_data"])
        raise
