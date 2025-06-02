from django import forms
from .models import *

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ["name", "openDate", "closeDate", "maxMarks", "noOfAttempts", "noOfQuestions", "skill", "tags", "is_practice"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Quiz Name"}),
            "openDate": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "closeDate": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "maxMarks": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Max Marks"}),
            "noOfAttempts": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Allowed Attempts"}),
            "noOfQuestions": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter Number of Questions"}),
            "skill": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
            "is_practice": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Additional custom validation logic if needed
        return cleaned_data

# forms.py
from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['name', 'description', 'answer_description', 'camp_category', 'skill', 'tags', 'is_practice']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'answer_description': forms.Textarea(attrs={'class': 'form-control', 'required': 'required'}),
            'camp_category': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'skill': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tags': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'is_practice': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['name', 'value']


from django import forms

class QuestionUploadForm(forms.Form):
    file = forms.FileField()


from django import forms
from .models import Skill, Tags

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = ['tag']