from rest_framework import serializers
from apps.resume.models import ResumeFile


class ResumeFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeFile
        fields = ['id', 'file', 'uploaded_at']
