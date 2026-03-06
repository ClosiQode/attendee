from cryptography.fernet import Fernet
from django.core.management.utils import get_random_secret_key


def generate_encryption_key():
    return Fernet.generate_key().decode("utf-8")


def generate_django_secret_key():
    return get_random_secret_key()


def main():
    credentials_key = generate_encryption_key()
    django_key = generate_django_secret_key()

    print(f"CREDENTIALS_ENCRYPTION_KEY={credentials_key}")
    print(f"DJANGO_SECRET_KEY={django_key}")
    print("AWS_RECORDING_STORAGE_BUCKET_NAME=")
    print("AWS_ACCESS_KEY_ID=")
    print("AWS_SECRET_ACCESS_KEY=")
    print("AWS_DEFAULT_REGION=us-east-1")
    print("BOT_SOFT_TIME_LIMIT_SECONDS=14400")
    print("")
    print("# Platform branding (white-label)")
    print("# PLATFORM_NAME=My Company")
    print("")
    print("# Hosting settings (update with your domain)")
    print("# SITE_DOMAIN=localhost:8000")
    print("# ALLOWED_HOSTS=localhost")
    print("# CSRF_TRUSTED_ORIGINS=https://your-domain.com")
    print("# DJANGO_SSL_REQUIRE=false")
    print("# DJANGO_DEBUG=true")
    print("")
    print("# Storage settings (uncomment for local storage)")
    print("# STORAGE_PROTOCOL=local")
    print("# LOCAL_RECORDING_STORAGE_PATH=/recordings")
    print("# LOCAL_AUDIO_CHUNK_STORAGE_PATH=/audio_chunks")


if __name__ == "__main__":
    main()
