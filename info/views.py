from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views import View
from interview_q.models import InterviewQuestion


class HomePageView(View):
    template_name = "info/home.html"
    def get(self, request, *args, **kwargs):
        featured_open_questions = InterviewQuestion.objects.filter(is_open=True)[:3]
        return render(request, self.template_name, {'questions': featured_open_questions})

class AboutPageView(TemplateView):

    template_name = "info/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TermsConditions(TemplateView):

    template_name = "info/terms_conditions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context