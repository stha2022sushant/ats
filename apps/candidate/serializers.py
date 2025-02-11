from rest_framework import serializers
from apps.candidate.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email', 'phone', 'address', 'parsed_text']
