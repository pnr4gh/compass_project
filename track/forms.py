from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Assignment, User_Handle


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile_no', 'batch', 'department', 'institute', 'github_link', 'linkedin_link']

    mobile_no = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}))
    github_link = forms.URLField(required=True, widget=forms.TextInput(attrs={'placeholder': 'GitHub Profile Link'}))
    linkedin_link = forms.URLField(required=True, widget=forms.TextInput(attrs={'placeholder': 'LinkedIn Profile Link'}))


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user   

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['name', 'start_date', 'end_date']

class UserHandleForm(forms.ModelForm):
    class Meta:
        model = User_Handle
        fields = ['platform', 'user_handle']  
    