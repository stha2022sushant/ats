from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.resume.models import ResumeFile
from apps.candidate.models import Candidate, Skill, CandidateSkill, Education, Experience, Project, AwardAndCertification
import pdfplumber
import fitz
import re
import os
from docx import Document


def extract_details(text):
    """
    Extracts name, email, phone, and address from resume text.
    """
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_regex = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    address_regex = r"([A-Za-z]+, Nepal)"

    emails = re.findall(email_regex, text)
    phones = re.findall(phone_regex, text)
    addresses = re.findall(address_regex, text)

    name = None
    lines = text.split("\n")
    for line in lines[:5]:  # Checking the first 5 lines for a name
        if len(line.split()) >= 2 and all(word[0].isupper() for word in line.split()):
            name = line.strip()
            break

    return {
        "name": name,
        "emails": emails,
        "phones": phones,
        "addresses": addresses
    }


def extract_section(text, section_name):
    """
    Extracts the 'KEY COMPETENCIES' section from the resume.
    """
    section_heading_pattern = re.compile(r'\b[A-Z ]+\b')
    headings = section_heading_pattern.findall(text)

    section_start = text.find(section_name)
    if section_start == -1:
        return ""

    section_end = len(text)
    for heading in headings:
        if heading != section_name and text.find(heading) > section_start:
            section_end = text.find(heading)
            break

    # section_content = text[section_start:section_end].strip()
    # return section_content.replace(section_name, "").strip()
    return text[section_start:section_end].replace(section_name, "").strip()


def extract_skills(text):
    """
    Extracts structured skills from the 'KEY COMPETENCIES' section.
    """
    competencies_section = extract_section(text, "KEY COMPETENCIES")
    skills = re.findall(r'\b[A-Za-z-]+\b', competencies_section)
    # competencies_lines = competencies_section.split('\n')
    return list(set(skills))


def extract_education(text):
    """
    Extract education details from the resume text.
    """
    education_section = extract_section(text, "EDUCATION") or extract_section(text, "ACADEMIC QUALIFICATIONS")
    education_entries = re.findall(r"([\w\s]+),\s*([\w\s]+),\s*(\d{4})-(\d{4})?", education_section)

    education_list = []
    for entry in education_entries:
        education_list.append({
            "institution_name": entry[0].strip(),
            "degree": entry[1].strip(),
            "start_date": f"{entry[2]}-01-01" if entry[2] else None,
            "end_date": f"{entry[3]}-12-31" if entry[3] else None
        })

    return education_list

# Experiences Sections


def extract_experience(text):
    """
    Extract work experience from the resume text.
    """
    experience_section = extract_section(text, "EXPERIENCE") or extract_section(text, "WORK EXPERIENCE")
    experience_entries = re.findall(r"([\w\s]+),\s*([\w\s]+),\s*(\d{4})-(\d{4})?", experience_section)

    experience_list = []
    for entry in experience_entries:
        experience_list.append({
            "company_name": entry[0].strip(),
            "job_title": entry[1].strip(),
            "start_date": f"{entry[2]}-01-01" if entry[2] else None,
            "end_date": f"{entry[3]}-12-31" if entry[3] else None
        })

    return experience_list

# Project Extractions


def extract_projects(text):
    """
    Extract project details from the resume text.
    """
    project_section = extract_section(text, "PROJECTS")
    project_entries = re.findall(r"([\w\s]+):\s*(.+)", project_section)

    projects_list = []
    for entry in project_entries:
        projects_list.append({
            "title": entry[0].strip(),
            "description": entry[1].strip()
        })

    return projects_list


# Extract Awards and Certifications


def extract_awards_and_certifications(text):
    """
    Extract awards and certifications from the resume text.
    """
    awards_section = extract_section(text, "AWARDS AND CERTIFICATIONS") or extract_section(text, "CERTIFICATIONS")

    awards_list = []
    award_entries = re.findall(r"([\w\s]+),\s*([\w\s]+),\s*(\d{4})?", awards_section)

    for entry in award_entries:
        awards_list.append({
            "name": entry[0].strip(),
            "issuing_organization": entry[1].strip(),
            "issue_date": f"{entry[2]}-01-01" if entry[2] else None
        })

    return awards_list


@receiver(post_save, sender=ResumeFile)
def parse_and_update_candidate(sender, instance, **kwargs):
    """
    Automatically parse resume content and update or create a Candidate record.
    """
    file_path = instance.file.path
    file_extension = os.path.splitext(file_path)[1].lower()

    text = ""

    if file_extension == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

    elif file_extension == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    extracted_data = extract_details(text)
    parsed_skills_section = extract_section(text, "KEY COMPETENCIES")
    extracted_skills = extract_skills(text)
    extracted_education = extract_education(text)
    extracted_experience = extract_experience(text)
    extracted_projects = extract_projects(text)
    extracted_awards = extract_awards_and_certifications(text)

    candidate, created = Candidate.objects.update_or_create(
        resume=instance,
        defaults={
            "name": extracted_data["name"],
            "email": extracted_data["emails"][0] if extracted_data["emails"] else None,
            "phone": extracted_data["phones"][0] if extracted_data["phones"] else None,
            "address": extracted_data["addresses"][0] if extracted_data["addresses"] else None,
            # "skills": ", ".join(extracted_skills) if extracted_skills else None,
            "parsed_text": text,
        },
    )

    for skill_name in extracted_skills:
        skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
        CandidateSkill.objects.update_or_create(
            candidate=candidate,
            skill=skill_obj,
            defaults={"proficiency_level": "Beginner", "years_of_experience": 0, "parsed_skills": parsed_skills_section}
        )

    for edu in extracted_education:
        Education.objects.update_or_create(
            candidate=candidate,
            institution_name=edu["institution_name"],
            degree=edu["degree"],
            defaults={
                "start_date": edu["start_date"],
                "end_date": edu["end_date"],
                "parsed_text": text
            }
        )

    for exp in extracted_experience:
        Experience.objects.update_or_create(
            candidate=candidate,
            company_name=exp["company_name"],
            job_title=exp["job_title"],
            defaults={
                "start_date": exp["start_date"],
                "end_date": exp["end_date"],
                "parsed_text": text
            }
        )

    for proj in extracted_projects:
        Project.objects.update_or_create(
            candidate=candidate,
            title=proj['title'],
            defaults={
                "description": proj["description"],
                "parsed_text": text
            }
        )

    for award in extracted_awards:
        AwardAndCertification.objects.update_or_create(
            candidate=candidate,
            name=award["name"],
            defaults={
                "issuing_organization": award["issuing_organization"],
                "issue_date": award["issue_date"],
                "parsed_text": text
            }
        )
