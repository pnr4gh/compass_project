from django import template
import os
from django.conf import settings
from track.models import Assignment, Solved_Problem, Assignment_Problems, Course_Enrollement
from django.contrib.auth.models import User


register = template.Library()

@register.filter(name='has_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 

@register.filter
def read_file(f):
    try:
        
        file=open(os.path.join(settings.BASE_DIR, f),'r')
        file_str = file.read()
        file.close()        
        return "\n" + file_str
    except IOError:
        return str(IOError)

@register.filter
def no_of_problems(user,assignment):
    
    try:
        ids = Assignment_Problems.objects.filter(assignment__id=assignment).values_list('problem__id',flat=True)
        
        count = Solved_Problem.objects.filter(problem__id__in=ids, user=user).count()
        return count
      
    except:
        pass

@register.filter
def is_solved(user,problem):
    
    try:
        return Solved_Problem.objects.filter(problem__id=problem, user=user).exists()
         
    except:
        pass

@register.filter
def problem_stat(course,problem):
    try:
        enrolled_users= Course_Enrollement.objects.filter(course=course).values_list('user',flat=True)
        return Solved_Problem.objects.filter(user__in=enrolled_users, problem=problem).count()
    except:
        pass


@register.filter
def filter_user_attempts(atttempts, user):
    return atttempts.filter(user=user)