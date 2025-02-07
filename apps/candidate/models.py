from django.db import models
from apps.resume.models import ResumeFile


class Candidate(models.Model):
    # Basic Information
    resume = models.OneToOneField(ResumeFile, on_delete=models.CASCADE, related_name="candidate")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    # Address Information
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    # Professional Details
    Linkedin_profile = models.URLField(null=True, blank=True)
    portfolio_website = models.URLField(null=True, blank=True)
    current_job_title = models.CharField(max_length=255, null=True, blank=True)
    current_employer = models.CharField(max_length=255, null=True, blank=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    skills = models.JSONField(null=True, blank=True)  # Store as a list
    certifications = models.JSONField(null=True, blank=True)

    # Educational Details
    highest_education = models.CharField(max_length=255, null=True, blank=True)
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)

    # Job Application Details
    # Job Application Details
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_date = models.DateField(null=True, blank=True)
    relocation_willingness = models.BooleanField(default=False)
    application_status = models.CharField(
        max_length=50,
        choices=[("Pending", "Pending"), ("Shortlisted", "Shortlisted"), ("Rejected", "Rejected"), ("Hired", "Hired")],
        default="Pending",
    )

    # Resume Relationship & Parsed Text
    # resume = models.ForeignKey(ResumeFile, on_delete=models.CASCADE, related_name="candidate", null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)  # Store raw extracted text for searching

    def __str__(self):
        return self.name or self.email
