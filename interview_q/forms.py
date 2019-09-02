from django import forms
from .models import InterviewQuestion

class InterviewQuestionCreationForm(forms.ModelForm):
    class Meta:
        model = InterviewQuestion
        fields = ('name', 'description')
