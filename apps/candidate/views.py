from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from apps.candidate.models import Candidate, CandidateSkill, Education, Experience, AwardAndCertification, Project
from apps.candidate.serializers import CandidateSerializer, CandidateSkillSerializer, EducationSerializer, ExperienceSerializer, AwardAndCertificationSerializer, ProjectSerializer


class CandidatePagination(PageNumberPagination):
    page_size = 10  # Default items per page
    page_size_query_param = 'page_size'
    max_page_size = 50


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    pagination_class = CandidatePagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'candidate_skills__skill__name': ['exact', 'icontains'],
        'experience__company_name': ['exact', 'icontains'],
        'education__institution_name': ['exact', 'icontains'],
        'education__degree': ['exact', 'icontains'],
    }
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'email', 'phone']


class CandidateSkillViewSet(viewsets.ModelViewSet):
    queryset = CandidateSkill.objects.all()
    serializer_class = CandidateSkillSerializer


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class AwardAndCertificationViewSet(viewsets.ModelViewSet):
    queryset = AwardAndCertification.objects.all()
    serializer_class = AwardAndCertificationSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
