from django.contrib import admin
from apps.candidate.models import Candidate, CandidateSkill, AwardAndCertification, Education, Experience, Project, Skill

admin.site.register(Candidate)
admin.site.register(CandidateSkill)
admin.site.register(AwardAndCertification)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Project)
admin.site.register(Skill)
