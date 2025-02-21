import os
import fitz
import pdfplumber
import re
from django.db.models.signals import post_save, post_delete
from docx import Document
from django.dispatch import receiver
from apps.resume.models import ResumeFile
from apps.candidate.models import Candidate, Skill, CandidateSkill, Education, Experience, Project, AwardAndCertification


def extract_details(text):
    """
    Extracts name, email, phone, and address from resume text.
    """
    # Normalize text: remove unnecessary newlines, multiple spaces
    clean_text = " ".join(text.split()).strip()

    # Regular expressions
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_regex = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    address_regex = r"([A-Za-z\s,-]+(?:Nepal|Kathmandu|Lalitpur|Bhaktapur))"

    # Extract details using regex
    emails = re.findall(email_regex, clean_text)
    phones = re.findall(phone_regex, clean_text)
    addresses = re.findall(address_regex, clean_text)

    # Extract name (first few lines checked)
    name = None
    lines = text.split("\n")  # Use line-based extraction for names
    for line in lines[:10]:  # Checking first 10 lines for a name
        line = line.strip()
        if (
            len(line.split()) >= 2  # At least two words
            and all(word[0].isupper() or word.lower() in ["de", "van", "mc"] for word in line.split())  # Handle lowercase prefixes
            and not any(keyword in line.lower() for keyword in ["email", "phone", "linkedin", "summary", "experience"])  # Exclude headers
        ):
            name = line
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
    Extracts education details from the resume text by locating the relevant section.
    """
    # Possible section headers for education
    education_section_names = ["EDUCATION", "ACADEMIC QUALIFICATIONS", "EDUCATIONAL BACKGROUND"]

    # Find the relevant section
    education_section = None
    for section in education_section_names:
        match = re.search(rf"{section}.*?\n(.*?)(?=\n[A-Z ]{{3,}}|\Z)", text, re.S | re.I)
        if match:
            education_section = match.group(1).strip()
            break  # Stop at the first found section

    if not education_section:
        return []

    # Patterns for degrees, institutions, and dates
    degree_patterns = r"(Bachelor|Master|PhD|Diploma|Associate|B\.Sc|M\.Sc|B\.A|M\.A|B\.E|M\.E|B\.Tech|M\.Tech)[^,\n]*"
    institution_patterns = r"([A-Za-z0-9 .,&-]+(?:University|College|Institute|School|Academy|Engineering College|Technology|Polytechnic))"
    date_patterns = r"(\d{4})\s*[-–]\s*(\d{4}|Present|Ongoing)"

    # Extract matches
    degrees = re.findall(degree_patterns, education_section, re.I)
    institutions = re.findall(institution_patterns, education_section)
    dates = re.findall(date_patterns, education_section)

    # Structuring the extracted education details
    education_data = []
    for i in range(max(len(degrees), len(institutions), len(dates))):
        degree = degrees[i] if i < len(degrees) else None
        institution = institutions[i] if i < len(institutions) else None
        start_date, end_date = dates[i] if i < len(dates) else (None, None)

        education_data.append({
            "degree": degree.strip() if degree else None,
            "institution": institution.strip() if institution else None,
            "start_date": start_date,
            "end_date": end_date
        })

    return education_data

# Experiences Sections


def extract_experience(text):
    """
    Extracts work experience details including job title, company name, and dates.
    """
    # Possible section headers for experience
    experience_section_names = ["WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT HISTORY", "EXPERIENCE"]

    # Find the relevant section
    experience_section = None
    for section in experience_section_names:
        match = re.search(rf"{section}.*?\n(.*?)(?=\n[A-Z ]{{3,}}|\Z)", text, re.S | re.I)
        if match:
            experience_section = match.group(1).strip()
            break  # Stop at the first found section

    if not experience_section:
        return []

    # Patterns for extracting job title, company, and dates
    job_title_pattern = r"(?:(?:Title|Position|Job)[:\s]*)?([A-Za-z0-9 ,&-]+)"
    company_pattern = r"(?:(?:Company|Employer)[:\s]*)?([A-Za-z0-9 ,&-]+)"
    date_patterns = r"(\d{4})\s*[-–]\s*(\d{4}|Present|Ongoing)"

    # Split experiences by bullet points or new lines
    experience_entries = re.split(r"\n\s*\n|\n[-•*]\s*", experience_section)

    experiences_data = []
    for entry in experience_entries:
        entry = entry.strip()
        if not entry:
            continue

        # Extract job title (first line or bolded text)
        title_match = re.match(job_title_pattern, entry)
        job_title = title_match.group(1).strip() if title_match else None

        # Extract company name (common words like "Company", "Inc.", etc.)
        company_match = re.search(company_pattern, entry)
        company_name = company_match.group(1).strip() if company_match else None

        # Extract dates
        date_match = re.search(date_patterns, entry)
        start_date, end_date = date_match.groups() if date_match else (None, None)

        # Store extracted experience details
        experiences_data.append({
            "job_title": job_title if job_title else None,
            "company_name": company_name if company_name else None,
            "start_date": start_date,
            "end_date": end_date,
            "parsed_experience": entry  # Store raw experience text
        })

    return experiences_data
# Project Extractions


def extract_projects(text):
    """
    Extracts project details including title, description, and dates.
    """
    # Possible section headers for projects
    project_section_names = ["PROJECTS", "PERSONAL PROJECTS", "RESEARCH PROJECTS", "WORK PROJECTS"]

    # Find the relevant section
    project_section = None
    for section in project_section_names:
        match = re.search(rf"{section}.*?\n(.*?)(?=\n[A-Z ]{{3,}}|\Z)", text, re.S | re.I)
        if match:
            project_section = match.group(1).strip()
            break  # Stop at the first found section

    if not project_section:
        return []

    # Patterns for project titles, descriptions, and dates
    project_title_pattern = r"(?:(?:Title|Project|Project Name)[:\s]*)?([A-Za-z0-9 ,&-]+)"
    date_patterns = r"(\d{4})\s*[-–]\s*(\d{4}|Present|Ongoing)"

    # Split projects by bullet points or new lines
    project_entries = re.split(r"\n\s*\n|\n[-•*]\s*", project_section)

    projects_data = []
    for entry in project_entries:
        entry = entry.strip()
        if not entry:
            continue

        # Extract project title (first bold text or first line)
        title_match = re.match(project_title_pattern, entry)
        title = title_match.group(1).strip() if title_match else None

        # Extract dates
        date_match = re.search(date_patterns, entry)
        start_date, end_date = date_match.groups() if date_match else (None, None)

        # Extract description (remaining text)
        description = entry.replace(title, "").strip() if title else entry.strip()

        projects_data.append({
            "title": title if title else None,
            "description": description if description else None,
            "start_date": start_date,
            "end_date": end_date,
            "parsed_project": entry  # Store raw project text
        })

    return projects_data


def extract_awards_and_certifications(text):
    """
    Extracts awards and certifications including name, issuing organization, and issue date.
    """
    # Possible section headers (more flexible)
    awards_certifications_section_names = [
        r"\bAWARDS\b", r"\bCERTIFICATIONS\b", r"\bHONORS & AWARDS\b",
        r"\bLICENSES & CERTIFICATIONS\b", r"\bACHIEVEMENTS\b", r"\bRECOGNITIONS\b"
    ]

    # Extracting the relevant section
    section_pattern = rf"({'|'.join(awards_certifications_section_names)})\s*\n(.*?)(?=\n[A-Z ]{{3,}}|\Z)"
    section_match = re.search(section_pattern, text, re.S | re.I)

    if not section_match:
        return []

    awards_certifications_section = section_match.group(2).strip()

    # Patterns for extracting award/certification details
    award_cert_name_pattern = r"^([\w\s,.'\-&()]+)"
    issuing_org_pattern = r"(?:by|from|issued by|provided by|offered by)\s+([\w\s,.'\-&()]+)"
    date_pattern = r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{1,2}/\d{4}|\b\d{4}\b)"

    # Splitting awards/certifications by bullet points or new lines
    award_cert_entries = re.split(r"\n\s*\n|\n[-•*]\s*", awards_certifications_section)

    awards_certifications_data = []
    for entry in award_cert_entries:
        entry = entry.strip()
        if not entry:
            continue

        # Extract award/certification name
        name_match = re.match(award_cert_name_pattern, entry)
        award_cert_name = name_match.group(1).strip() if name_match else None

        # Extract issuing organization
        org_match = re.search(issuing_org_pattern, entry)
        issuing_organization = org_match.group(1).strip() if org_match else None

        # Extract issue date
        date_match = re.search(date_pattern, entry)
        issue_date = date_match.group(1) if date_match else None

        # Store extracted awards/certifications details
        awards_certifications_data.append({
            "name": award_cert_name if award_cert_name else None,
            "issuing_organization": issuing_organization if issuing_organization else None,
            "issue_date": issue_date,
            "parsed_awards_and_certifications": entry  # Store raw text for reference
        })

    return awards_certifications_data


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
            institution_name=edu["institution"],
            degree=edu["degree"],
            defaults={
                "start_date": edu["start_date"],
                "end_date": edu["end_date"],
                "parsed_text": text,
                # "parsed_edu": edu["parsed_experience_text"]
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


@receiver(post_delete, sender=ResumeFile)
def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes the file from storage when a ResumeFile object is deleted."""
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
