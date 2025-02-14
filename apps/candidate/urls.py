from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CandidateViewSet, CandidateSkillViewSet, EducationViewSet, ExperienceViewSet, AwardAndCertificationViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'candidateskills-', CandidateSkillViewSet, basename='candidate-skill')
router.register(r'education', EducationViewSet, basename='education')
router.register(r'experience', ExperienceViewSet, basename='experience')
router.register(r'awards-certifications', AwardAndCertificationViewSet, basename='awards-certifications')
router.register(r'projects', ProjectViewSet, basename='projects')

urlpatterns = [
    path('', include(router.urls)),
]
