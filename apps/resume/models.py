from django.db import models
import os
from config.settings import file_upload_validator


class ResumeFile(models.Model):
    file = models.FileField(upload_to='uploads/', validators=[file_upload_validator])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            existing = ResumeFile.objects.filter(pk=self.pk).first()
            if existing and existing.file != self.file:
                if os.path.isfile(existing.file.path):
                    os.remove(existing.file.path)
        super().save(*args, **kwargs)
   
    def __str__(self):
        return self.file.name
