from rest_framework import viewsets
from apps.resume.models import ResumeFile
from apps.resume.serializers import ResumeFileSerializer


class ResumeFileViewSet(viewsets.ModelViewSet):
    queryset = ResumeFile.objects.all()
    serializer_class = ResumeFileSerializer
