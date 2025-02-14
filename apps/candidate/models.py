from django.db import models
from apps.resume.models import ResumeFile


class Candidate(models.Model):
    # Basic Information
    resume = models.OneToOneField(ResumeFile, on_delete=models.CASCADE, related_name="candidate")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    Linkedin_profile = models.URLField(null=True, blank=True)
    portfolio_website = models.URLField(null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)  # Store raw extracted text for searching

    def __str__(self):
        return self.name or self.email


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CandidateSkill(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name="candidate_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="candidate_skills")
    parsed_skills = models.TextField(null=True, blank=True)  # Store raw extracted text for searching

    proficiency_level = models.CharField(max_length=50, null=True, blank=True, choices=[
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert')
    ])

    years_of_experience = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.candidate.name} - {self.skill.name} ({self.proficiency_level})"


class Education(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="education")
    institution_name = models.CharField(max_length=50, null=True, blank=True)
    degree = models.CharField(max_length=20, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)  # Store raw extracted text for searching

    def __str__(self):
        degree = self.degree if self.degree else "Unknown Degree"
        institution = self.institution_name if self.institution_name else "Unknown Institution"
        return f"{degree} at {institution}"


class Experience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experience")
    company_name = models.CharField(max_length=25, null=True, blank=True)
    job_title = models.CharField(max_length=50, null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        job_title = self.job_title if self.job_title else "Unknown Job Title"
        company_name = self.company_name if self.company_name else "Unknown Company"
        return f"{job_title} position at {company_name}"


class AwardAndCertification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="awards_certifications")
    name = models.CharField(max_length=150, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    issuing_organization = models.CharField(max_length=100, null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)

    def __str__(self):
        name = self.name if self.name else "Unknown Issue Date"
        issuing_organization = self.issuing_organization if self.issuing_organization else "Unknown Issuing Organization"
        return f"{name} by {issuing_organization}"


class Project(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    parsed_text = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        title = self.title if self.title else "Unknown Title"
        start_date = self.start_date if self.start_date else "Unknown Start Date"
        end_date = self.end_date if self.end_date else "Unknown End Date"
        return f"{title} from {start_date} - {end_date}"
