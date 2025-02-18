import os
import magic
from django.core.exceptions import ValidationError


ALLOWED_EXTENSIONS = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE_MB = 5


def file_upload_validator(file):
    ext = os.path.splitext(file.name)[1][1:].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}")

    mime_detector = magic.Magic(mime=True)
    file_mime_type = mime_detector.from_buffer(file.read(2048))
    file.seek(0)

    if file_mime_type != ALLOWED_EXTENSIONS[ext]:
        raise ValidationError(f"Invalid file format. Expected {ALLOWED_EXTENSIONS[ext]}, but got {file_mime_type}")

    file_size = file.size
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.")

    return file
