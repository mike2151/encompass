from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .forms import InterviewQuestionCreationForm
from .models import InterviewQuestion
from interview_code_file.models import InterviewCodeFile
from interview_test_case.models import InterviewTestCase
from interview_q_instance.models import InterviewQuestionInstance
from api_q.models import InterviewAPI
from example_code.models import ExampleCode
from method_signature.models import MethodSignature
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .utils import is_valid_test_case

class CreateInterviewView(View):
    template_name = 'interview_q/create.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        name = self.request.POST.get('name', '')
        description = self.request.POST.get('description', '')
        is_open = self.request.POST.get('is_open', False)
        question_language = self.request.POST.get('question_language', '')
        solution = self.request.POST.get('solution', '')
        starter_code = self.request.POST.get('starter_code', '')
        if len(name) == 0:
            return render(request, self.template_name, {"error_message": "name field not filled out"})
        if len(description) == 0:
            return render(request, self.template_name, {"error_message": "description field not filled out"})
        question = InterviewQuestion(name=name, description=description, creator=self.request.user, is_open=is_open, language=question_language, solution=solution, starter_code=starter_code)
        question.save()

        question_id = question.id
        
        # handle supporting code
        supporting_code = self.request.POST.get("supporting_code", "")
        interview_code_file = InterviewCodeFile(body=supporting_code, interview_question=question)
        interview_code_file.save()

        api_description = self.request.POST.get("api_description", "")

        # handle api methods
        curr_api_method = 1
        curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')
        while (len(curr_field) > 0):
            # create new API object if first field
            if curr_api_method == 1:
                api = InterviewAPI(description=api_description)
                api.save()
                i_question = InterviewQuestion.objects.get(pk=question_id)
                i_question.api = api
                i_question.save()
            # create new method object
            method = MethodSignature(api_signature=curr_field, interview_question_api=api)
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

        # handle test cases
        all_test_cases_str = self.request.POST.get('test_cases', '')
        all_test_cases = all_test_cases_str.split("\n\n")
        if len(all_test_cases) > 0:
            curr_test_case_num = 0
            curr_test_case = all_test_cases[curr_test_case_num]
            while (len(curr_test_case) > 0):
                if is_valid_test_case(curr_test_case):
                    test_case = InterviewTestCase(body=curr_test_case, interview_question=question)
                    test_case.save()
                    curr_test_case_num = curr_test_case_num + 1
                    if (curr_test_case_num == len(all_test_cases)):
                        break
                    curr_test_case = all_test_cases[curr_test_case_num]

        return HttpResponseRedirect("/interview_questions/")


class HomeInterviewView(ListView):
    model = InterviewQuestion
    template_name = 'interview_q/all.html'
    context_object_name = 'interview_questions'        

    def get_queryset(self):
        return InterviewQuestion.objects.all()


class EditQuestionView(View):
    template_name = "interview_q/question.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'question': question})
    def post(self, request,  *args, **kwargs):
        name = self.request.POST.get('name', '')
        description = self.request.POST.get('description', '')
        is_open = self.request.POST.get('is_open', False)
        question_language = self.request.POST.get('question_language', '')
        solution = self.request.POST.get('solution', '')
        starter_code = self.request.POST.get('starter_code', '')
        if len(name) == 0:
            return render(request, self.template_name, {"error_message": "name field not filled out"})
        if len(description) == 0:
            return render(request, self.template_name, {"error_message": "description field not filled out"})
        question_id = kwargs['pk']
        question = InterviewQuestion.objects.get(pk=question_id)
        question.save()

        question_id = question.id
        
        # handle supporting code
        supporting_code = self.request.POST.get("supporting_code", "")
        interview_code_file = InterviewCodeFile(body=supporting_code, interview_question=question)
        interview_code_file.save()

        api_description = self.request.POST.get("api_description", "")

        # handle api methods
        curr_api_method = 1
        curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')
        while (len(curr_field) > 0):
            # create new API object if first field
            if curr_api_method == 1:
                api = InterviewAPI(description=api_description)
                api.save()
                i_question = InterviewQuestion.objects.get(pk=question_id)
                i_question.api = api
                i_question.save()
            # create new method object
            method = MethodSignature(api_signature=curr_field, interview_question_api=api)
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

        # handle test cases
        all_test_cases_str = self.request.POST.get('test_cases', '')
        all_test_cases = all_test_cases_str.split("\n\n")
        if len(all_test_cases) > 0:
            curr_test_case_num = 0
            curr_test_case = all_test_cases[curr_test_case_num]
            while (len(curr_test_case) > 0):
                if is_valid_test_case(curr_test_case):
                    test_case = InterviewTestCase(body=curr_test_case, interview_question=question)
                    test_case.save()
                    curr_test_case_num = curr_test_case_num + 1
                    if (curr_test_case_num == len(all_test_cases)):
                        break
                    curr_test_case = all_test_cases[curr_test_case_num]

        return HttpResponseRedirect("/interview_questions/")

class CreateQuestionInstanceView(View):
    template_name = "interview_q/send.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        return render(request, self.template_name, {'question': question})
    def post(self, request,  *args, **kwargs):
        user_email = self.request.POST.get('email', '')
        base_question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        if len(user_email) == 0:
            return render(request, self.template_name, {"error_message": "email field not filled out"})
        
        start_date_field = self.request.POST.get('start_date', '')

        question_instance = InterviewQuestionInstance(interviewee_email=user_email, base_question=base_question, start_time=start_date_field)
        question_instance.save()
        return HttpResponseRedirect("/interview_questions/")
        