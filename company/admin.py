from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Company)
admin.site.register(JobRole)
admin.site.register(InterviewProcess)
admin.site.register(Skill)
admin.site.register(Round_Skills)
admin.site.register(Round_Skill_Detail)
admin.site.register(SalaryBand)
