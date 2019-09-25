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

        error_messages = []
        if password != password2:
            error_messages.append("passwords do not match")

        if len(password) < 8:
            error_messages.append("passwords must be longer than 8 characters")

        email_taken = True
        try:
            _ = SiteUser.objects.get(email=email)
        except SiteUser.DoesNotExist:
            email_taken = False

        if email_taken:
            error_messages.append("email taken")
        
        if len(error_messages) > 0:
            return render(request, self.template_name, {"error_messages": error_messages})

        is_from_company = request.POST.get('is_from_company', '') == 'on'
        if is_from_company:
            company_org = request.POST.get('comp_org', '')
            user = SiteUser.objects.create_user(username=email, email=email, password=password, company_org=company_org, is_from_company=True)
        else:
            user_role = request.POST.get('user_role', '')
            user = SiteUser.objects.create_user(username=email, email=email, password=password, user_role=user_role)
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
            return render(request, self.template_name, {"invalid_login": True})