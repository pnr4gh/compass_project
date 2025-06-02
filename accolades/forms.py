
from django import forms
from .models import Accolade, Organization, Outcome, Scope

from django import forms
from .models import Accolade

from django import forms
from .models import Accolade

class AccoladeForm(forms.ModelForm):
    class Meta:
        model = Accolade
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'What do you want to talk about?', 'rows': 10}),
        }
        

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name']
