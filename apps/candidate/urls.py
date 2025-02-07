from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.candidate.views import CandidateViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet)

urlpatterns = router.urls
