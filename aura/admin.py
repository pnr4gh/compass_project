from django.contrib import admin
from .models import Skill, Tags, Quiz, Question, Response,Attempt,User_Score,Option
# Register your models here.
admin.site.register(Skill)
admin.site.register(Tags)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Attempt)
admin.site.register(User_Score)
admin.site.register(Option)