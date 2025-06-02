from django.contrib import admin
from . import models

# Register your models here.

class ProblemAdmin(admin.ModelAdmin):
    
   
    search_fields = ['problem_title','problem_slug']
    
    
admin.site.register(models.Platform)

admin.site.register(models.Problem,ProblemAdmin)
admin.site.register(models.Profile)
admin.site.register(models.Department)
admin.site.register(models.Batch)
admin.site.register(models.Institution)
admin.site.register(models.Solved_Problem)
admin.site.register(models.User_Handle)
admin.site.register(models.ProblemTags)
admin.site.register(models.Assignment)
admin.site.register(models.Assignment_Problems)
admin.site.register(models.Course)
admin.site.register(models.Course_Enrollement)
admin.site.register(models.Complexity)
admin.site.register(models.Tags)
admin.site.register(models.ProblemType)
admin.site.register(models.ProblemStats)
admin.site.register(models.Contest)

admin.site.register(models.discussion_detail)