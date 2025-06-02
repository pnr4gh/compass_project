from django.db import models
from track.models import *


# Company Hiring Process (Company Details)

class Company(models.Model):
    name = models.CharField(max_length=200)
    company_type = models.CharField(
        max_length=50,
        choices=[
            ('SERVICE', 'Service Based'),
            ('PRODUCT', 'Product Based')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class JobRole(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_roles')
    title = models.CharField(max_length=100) 
    package_in_LPA = models.DecimalField(max_digits=12, decimal_places=2)
    job_description = models.TextField(max_length=300)
    hiring_process = models.CharField(
        max_length=50,
        choices=[
            ('CONTEST', 'Contest Hiring'),
            ('CAMPUS', 'Campus Hiring')
        ]
    )
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name} - {self.title}"

class InterviewProcess(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='interview_process')
    round_name = models.CharField(max_length=100)
    round_number = models.PositiveIntegerField()
    round_type = models.CharField(
        max_length=50,
        choices=[
            ('SYSTEM', 'system'),
            ('VIRTUAL_FACE_TO_FACE', 'virtual_face_to_face'),
            ('FACE_TO_FACE', 'face_to_face'),
        ]
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.job_role} - Round {self.round_number} ({self.get_round_type_display()})"


class Skill(models.Model):
    skill = models.CharField(max_length=100)

    def __str__(self):
        return self.skill

class Round_Skills(models.Model):
    interview_round = models.ForeignKey(InterviewProcess, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='round_skills')

    def __str__(self):
        return f"{self.interview_round} - {self.skill_name}"

class Round_Skill_Detail(models.Model):
    round_skill = models.ForeignKey(Round_Skills, on_delete=models.CASCADE, related_name='round_skill')
    tags = models.ForeignKey(Tags, on_delete=models.CASCADE, related_name='round_tags')
    weight = models.IntegerField()

    def __str__(self):
        return f"{self.round_skill} - {self.tags}"        

class SalaryBand(models.Model):
    salary_range = models.CharField(max_length=50, unique=True, help_text="e.g., '0-3 ', '3-6'")
   
    companies = models.ManyToManyField(
        'Company',
        related_name='salary_bands',
        help_text="Companies associated with this salary band"
    )
    
    def __str__(self):
        return f"{self.salary_range} LPA "