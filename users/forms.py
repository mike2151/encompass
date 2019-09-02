from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import SiteUser

class SiteUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = SiteUser
        fields = ('email',)

class SiteUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = SiteUser
        fields = ('email',)