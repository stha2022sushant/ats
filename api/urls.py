from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ats.views import UploadedFileViewSet, parse_pdf

router = DefaultRouter()
router.register(r'uploads', UploadedFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('parse-pdf/<int:file_id>/', parse_pdf, name='parse-pdf'),
]
