from pathlib import Path

from django.core.exceptions import ValidationError


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 25 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}

ALLOWED_DOCUMENT_EXTENSIONS = {".pdf"}
ALLOWED_DOCUMENT_MIME_TYPES = {"application/pdf"}

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}
ALLOWED_VIDEO_MIME_TYPES = {"video/mp4", "video/webm", "video/ogg"}


def _file_extension(value):
    return Path(value.name).suffix.lower()


def _file_mime(value):
    return getattr(value, "content_type", "")


def validate_image_upload(value):
    ext = _file_extension(value)
    mime_type = _file_mime(value)

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Format image non autorise. Utilisez jpg, jpeg, png ou webp.")
    if mime_type and mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError("Type MIME image non autorise.")
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError("Image trop volumineuse (max 5 MB).")


def validate_document_upload(value):
    ext = _file_extension(value)
    mime_type = _file_mime(value)

    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError("Seuls les fichiers PDF sont autorises.")
    if mime_type and mime_type not in ALLOWED_DOCUMENT_MIME_TYPES:
        raise ValidationError("Type MIME document non autorise.")
    if value.size > MAX_DOCUMENT_SIZE:
        raise ValidationError("Document trop volumineux (max 10 MB).")


def validate_video_upload(value):
    ext = _file_extension(value)
    mime_type = _file_mime(value)

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError("Format video non autorise. Utilisez mp4, webm ou ogg.")
    if mime_type and mime_type not in ALLOWED_VIDEO_MIME_TYPES:
        raise ValidationError("Type MIME video non autorise.")
    if value.size > MAX_VIDEO_SIZE:
        raise ValidationError("Video trop volumineuse (max 25 MB).")
