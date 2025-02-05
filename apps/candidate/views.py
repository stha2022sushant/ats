from rest_framework import viewsets
from apps.candidate.models import Candidate
from apps.candidate.serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
