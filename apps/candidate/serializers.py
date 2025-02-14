from rest_framework import serializers
from apps.candidate.models import Candidate, CandidateSkill, Skill, Education, Experience, Project, AwardAndCertification

"""
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'email', 'phone', 'address', 'parsed_text']


class CandidateSkillSerializers(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')

    class Meta:
        model = CandidateSkill
        fields = ['skill_name', 'proficiency_level', 'years_of_experience']


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'start_date', 'end_date']

"""


class CandidateSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = CandidateSkill
        fields = ['id', 'skill', 'skill_name', 'proficiency_level', 'years_of_experience', 'parsed_skills']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['institution_name', 'degree', 'parsed_text']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['company_name', 'job_title', 'parsed_text']


class AwardAndCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AwardAndCertification
        fields = ['name', 'issuing_organization', 'parsed_text']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'parsed_text']


class CandidateSerializer(serializers.ModelSerializer):
    candidate_skills = CandidateSkillSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    awards_certifications = AwardAndCertificationSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id', 'resume', 'name', 'email', 'phone', 'address', 'Linkedin_profile', 'portfolio_website', 'parsed_text',
            'candidate_skills', 'education', 'experience', 'awards_certifications', 'projects'
        ]
