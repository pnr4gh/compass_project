from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Skill(models.Model):
    skill = models.CharField(max_length=256)
    def __str__(self):
        return self.skill
    
    
    
class Tags(models.Model):
    tag = models.CharField(max_length=256)
    def __str__(self):
        return self.tag





class Quiz(models.Model):
    name = models.CharField(max_length=150)
    
    openDate = models.DateField()
    closeDate = models.DateField(null=True,blank=True)
    maxMarks= models.IntegerField(null=True,blank=True)
    isActive= models.BooleanField(default=True)
    noOfAttempts=models.IntegerField(null=True,blank=True,default=2)
    noOfQuestions=models.IntegerField(null=True,blank=True)
    skill=models.ForeignKey(Skill,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags)
    is_practice=models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-id',)


class Question(models.Model):
    camp_category_choices =  (
        ('C', 'Conceptual'),
        ('A', 'Analytical '),
        ('M', 'Memory'),
        ('P', 'Practice')
    )
    name = models.CharField(max_length=225)
    description = RichTextField()  
    answer_description=models.CharField(max_length=500,null=True)
    camp_category = models.CharField(max_length=1,null=True, choices=camp_category_choices)
    skill=models.ForeignKey(Skill,on_delete=models.CASCADE)
    tags=models.ForeignKey(Tags,on_delete=models.CASCADE)
    is_practice=models.BooleanField(default=True)
    

    def __str__(self):
        return self.name + self.camp_category

    @property
    def options(self):
        return self.option_set.values()
    
    @property
    def answers(self):
        return self.option_set.filter(value=1)
    

class Option(models.Model):
    name = models.TextField()
    value = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)  # ✅ Renamed to lowercase

    def __str__(self):
        return self.name


class Attempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)  # Renamed to lowercase
    score = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    attemptNo = models.IntegerField()    

 
class User_Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_score = models.CharField(max_length=4)
    quiz=models.ForeignKey(Quiz,on_delete=models.CASCADE,null=True)
    date=models.DateTimeField(auto_now_add=True,null=True)
    
    
    def __self__(self):
    	return self.user_score
    	

class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Option=models.ForeignKey(Option,on_delete=models.CASCADE)
    Question=models.ForeignKey(Question,on_delete=models.CASCADE)
    Attempt=models.ForeignKey(Attempt,on_delete=models.CASCADE,null=True)
    user_score=models.ForeignKey(User_Score,on_delete=models.CASCADE,null=True)