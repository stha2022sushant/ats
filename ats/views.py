# from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse
import pdfplumber
import re
from ats.models import UploadedFile
from api.serializers import UploadedFileSerializer


class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer


def extract_details(text):
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_regex = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"

    emails = re.findall(email_regex, text)
    phones = re.findall(phone_regex, text)

    name = None
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line.split()) >= 2 and all(word[0].isupper() for word in line.split()):
            name = line.strip()
            break

    return {"name": name, "emails": emails, "phones": phones}


def parse_pdf(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        file_path = uploaded_file.file.path

        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        extracted_data = extract_details(text)

        return JsonResponse({"extracted_data": extracted_data})

    except UploadedFile.DoesNotExist:
        return JsonResponse({"error": "File not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
