from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.resume.views import ResumeFileViewSet

router = DefaultRouter()
router.register(r'uploads', ResumeFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('parse-file/<int:file_id>/', parse_file, name='parse-file'),
]
