from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .forms import InterviewQuestionCreationForm
from .models import InterviewQuestion
from api_q.models import InterviewAPI
from example_code.models import ExampleCode
from method_signature.models import Method
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render

class CreateInterviewView(View):
    template_name = 'interview_q/create.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        name = self.request.POST.get('name', '')
        description = self.request.POST.get('description', '')
        if len(name) == 0:
            return render(request, self.template_name, {"error_message": "name field not filled out"})
        if len(description) == 0:
            return render(request, self.template_name, {"error_message": "description field not filled out"})
        question = InterviewQuestion(name=name, description=description, creator=self.request.user)
        question.save()
        api_description = self.request.POST.get("api_description", "")

        # handle api methods
        curr_api_method = 1
        curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')
        while (len(curr_field) > 0):
            # create new API object if first field
            if curr_api_method == 1:
                api = InterviewAPI(description=api_description)
                api.save()
            # create new method object
            method = Method(body=curr_field, interview_question_api=api)
            method.save()
            curr_api_method = curr_api_method + 1
            curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')

        # handle example code
        curr_code_body_num = 1
        curr_body = self.request.POST.get('code_body_' + str(curr_code_body_num), '')
        while (len(curr_body) > 0):
            example_code = ExampleCode(body=curr_body, interview_question=question)
            example_code.save()
            curr_code_body_num = curr_code_body_num + 1
            curr_body = self.request.POST.get('code_body_' + str(curr_code_body_num), '')

        return HttpResponseRedirect("/interview_questions/")


class HomeInterviewView(ListView):
    model = InterviewQuestion
    template_name = 'interview_q/all.html'
    context_object_name = 'interview_questions'        

    def get_queryset(self):
        return InterviewQuestion.objects.all()


class IndividualQuestionView(View):
    template_name = "interview_q/question.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'question': question})

class CreateQuestionInstanceView(View):
    template_name = "interview_q/create_instance.html"