from django.db import models
from configs.settings import file_upload_validator


class ResumeFile(models.Model):
    file = models.FileField(upload_to='uploads/', validators=[file_upload_validator])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
