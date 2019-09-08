# users/views.py
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import SiteUser
from django.contrib.auth import authenticate, login


class SignUpView(View):
    template_name = 'registration/signup.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        password2 = self.request.POST.get('password2', '')
        user = SiteUser.objects.create_user(username=email, email=email, password=password)
        return HttpResponseRedirect("/users/login/")

class LoginView(View):
    template_name = 'registration/login.html'   
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        print(user)
        if user:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect("/users/login")