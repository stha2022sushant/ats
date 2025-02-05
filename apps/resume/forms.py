from django import forms
from apps.resume.models import ResumeFile


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeFile
        fields = ['file']
