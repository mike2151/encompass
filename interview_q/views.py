from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .forms import InterviewQuestionCreationForm
from .models import InterviewQuestion
from interview_code_file.models import SupportCode
from interview_test_case.models import InterviewTestCase
from interview_q_instance.models import InterviewQuestionInstance
from api_q.models import InterviewAPI
from example_code.models import ExampleCode
from method_signature.models import MethodSignature
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .utils import is_valid_test_case
from datetime import datetime, timedelta
from django.core.files.base import ContentFile
from starter_code.models import StarterCode
from solution_code.models import SolutionCode
from interview_q_instance.util import create_and_run_submission
import pytz


class CreateInterviewView(View):
    def check_condition(self, request, name, number):
        cond_one = (len(request.POST.get(name + "_body_name_" + str(number), '')) > 0 and len(request.POST.get(name + "_body_" + str(number), '')) > 0)
        cond_two = request.FILES.get(name + "_file_" + str(number), False)
        return cond_one or cond_two

    template_name = 'interview_q/create.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            name = self.request.POST.get('name', '')
            description = self.request.POST.get('description', '')
            is_open = self.request.POST.get('is_open', '') == 'on'
            question_language = self.request.POST.get('question_language', '')
            if len(name) == 0:
                return render(request, self.template_name, {"error_message": "name field not filled out"})
            if len(description) == 0:
                return render(request, self.template_name, {"error_message": "description field not filled out"})
            question = InterviewQuestion(name=name, description=description, creator=self.request.user, is_open=is_open, language=question_language)
            question.save()

            question_id = question.id
            
            # handle supporting code
            name = "supporting"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = SupportCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = SupportCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1
            

            api_description = self.request.POST.get("api_description", "")

            # handle api methods
            curr_api_method = 1
            curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')
            while (len(curr_field) > 0):
                # create new API object if first field
                if curr_api_method == 1:
                    api = InterviewAPI(description=api_description, interview_question=question)
                    api.save()
                # create new method object
                method = MethodSignature(api_signature=curr_field, interview_question_api=api)
                method.save()
                curr_api_method = curr_api_method + 1
                curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')

            # handle starter code
            name = "starter"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = StarterCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = StarterCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1

            # handle example code
            name = "example"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = ExampleCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = ExampleCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1


            # handle test cases
            name = "test"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = InterviewTestCase(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = InterviewTestCase(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1

            # handle solution
            submitted_solution = False
            name = "solution"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = SolutionCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                        submitted_solution = True
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = SolutionCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                        submitted_solution = True
                number = number + 1

            if submitted_solution:
                return HttpResponseRedirect("/interview_questions/question/" + str(question_id) + "/validate/")

            return HttpResponseRedirect("/interview_questions/")
        else:
            return HttpResponseRedirect("/")

class HomeInterviewView(View):
    template_name = 'interview_q/all.html'
    def get(self, request, *args, **kwargs):
        questions = []
        if request.user.is_authenticated:
            questions = InterviewQuestion.objects.filter(creator=request.user)
        return render(request, self.template_name, {'interview_questions': questions})

class DeleteQuestionView(View):
    template_name = 'interview_q/delete.html'
    def get(self, request, *args, **kwargs):
        question = None
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'question': question})
    def post(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        if request.user.is_authenticated:
            if request.user == question.creator:
                question.delete()
        return HttpResponseRedirect("/interview_questions/")

class EditQuestionView(View):
    def check_condition(self, request, name, number):
        cond_one = (len(request.POST.get(name + "_body_name_" + str(number), '')) > 0 and len(request.POST.get(name + "_body_" + str(number), '')) > 0)
        cond_two = request.FILES.get(name + "_file_" + str(number), False)
        return cond_one or cond_two

    template_name = "interview_q/question.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))

        supporting_code = SupportCode.objects.filter(interview_question=question)
        supporting_code_names = []
        supporting_code_contents = []
        for support_code in supporting_code:
            supporting_code_names.append(support_code.code_file.name.split("/")[-1])
            support_code.code_file.open(mode='r') 
            contents = support_code.code_file.read()
            support_code.code_file.close()
            supporting_code_contents.append(contents)

        starter_code_all = StarterCode.objects.filter(interview_question=question)
        starter_code_names = []
        starter_code_contents = []
        for starter_code in starter_code_all:
            starter_code_names.append(starter_code.code_file.name.split("/")[-1])
            starter_code.code_file.open(mode='r') 
            contents = starter_code.code_file.read()
            starter_code.code_file.close()
            starter_code_contents.append(contents)

        example_code_all = ExampleCode.objects.filter(interview_question=question)
        example_code_names = []
        example_code_contents = []
        for example_code in example_code_all:
            example_code_names.append(example_code.code_file.name.split("/")[-1])
            example_code.code_file.open(mode='r') 
            contents = example_code.code_file.read()
            example_code.code_file.close()
            example_code_contents.append(contents)

        test_case = InterviewTestCase.objects.filter(interview_question=question).first()
        test_case_name = ""
        test_case_code_contents = ""
        if test_case is not None:
            test_case_name = test_case.code_file.name.split("/")[-1]
            test_case.code_file.open(mode='r') 
            test_case_code_contents = test_case.code_file.read()
            test_case.code_file.close()

        solution_code_all = SolutionCode.objects.filter(interview_question=question)
        solution_code_names = []
        solution_code_contents = []
        for solution_code in solution_code_all:
            solution_code_names.append(solution_code.code_file.name.split("/")[-1])
            solution_code.code_file.open(mode='r') 
            contents = solution_code.code_file.read()
            solution_code.code_file.close()
            solution_code_contents.append(contents)

        api = InterviewAPI.objects.filter(interview_question=question).first()
        api_description = ""
        if api is not None:
            api_description = api.description

        api_methods = MethodSignature.objects.filter(interview_question_api=api)

        return render(request, self.template_name, {
            'question': question, 
            'supporting_code_names': supporting_code_names,
            'supporting_code_contents': supporting_code_contents,
            'starter_code_names': starter_code_names,
            'starter_code_contents': starter_code_contents,
            'solution_code_names': solution_code_names,
            'solution_code_contents': solution_code_contents,
            'api_description': api_description,
            'test_case_name': test_case_name,
            'test_case_code_contents': test_case_code_contents,
            'example_code_names': example_code_names,
            'example_code_contents': example_code_contents,
            'api_methods': api_methods
        })
    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            name = self.request.POST.get('name', '')
            description = self.request.POST.get('description', '')
            is_open = self.request.POST.get('is_open', '') == 'on'
            question_language = self.request.POST.get('question_language', '')
            if len(name) == 0:
                return render(request, self.template_name, {"error_message": "name field not filled out"})
            if len(description) == 0:
                return render(request, self.template_name, {"error_message": "description field not filled out"})
            question_id = kwargs['pk']
            question = InterviewQuestion.objects.get(pk=question_id)
            
            # replace basic fields
            question.name = name
            question.description = description
            question.language = question_language
            question.is_open = is_open

            question.save()
            question_id = question.id

            # delete existing models
            api = InterviewAPI.objects.filter(interview_question=question).first()
            if api is not None:
                MethodSignature.objects.filter(interview_question_api=api).delete()
                api.delete()

            ExampleCode.objects.filter(interview_question=question).delete()
            SupportCode.objects.filter(interview_question=question).delete()
            InterviewTestCase.objects.filter(interview_question=question).delete()
            SolutionCode.objects.filter(interview_question=question).delete()
            StarterCode.objects.filter(interview_question=question).delete()
 
 
            # repeat code above in create

            # handle supporting code
            name = "supporting"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = SupportCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = SupportCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1
            

            api_description = self.request.POST.get("api_description", "")

            # handle api methods
            curr_api_method = 1
            curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')
            while (len(curr_field) > 0):
                # create new API object if first field
                if curr_api_method == 1:
                    api = InterviewAPI(description=api_description, interview_question=question)
                    api.save()
                # create new method object
                method = MethodSignature(api_signature=curr_field, interview_question_api=api)
                method.save()
                curr_api_method = curr_api_method + 1
                curr_field = self.request.POST.get('api_method_' + str(curr_api_method), '')

            # handle starter code
            name = "starter"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = StarterCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = StarterCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1

            # handle example code
            name = "example"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = ExampleCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = ExampleCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1


            # handle test cases
            name = "test"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = InterviewTestCase(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = InterviewTestCase(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1

            # handle solution
            name = "solution"
            number = 1
            while self.check_condition(request, name, number):
                if request.POST.get(name + "_switch_" + str(number), False):
                    # file
                    if request.FILES.get(name + "_file_" + str(number), False):
                        new_file = SolutionCode(code_file=request.FILES[name + "_file_" + str(number)], interview_question=question)
                        new_file.save()
                else:
                    # code
                    # write to file
                    file_name = request.POST.get(name + "_body_name_" + str(number),'')
                    file_contents = request.POST.get(name + "_body_" + str(number),'')
                    if len(file_name) > 0 and len(file_contents) > 0:
                        new_file = SolutionCode(interview_question=question)
                        new_file.code_file.save(file_name, ContentFile(file_contents))
                        new_file.save()    
                number = number + 1
            return HttpResponseRedirect("/interview_questions/")
        else:
            return HttpResponseRedirect("/")

class CreateQuestionInstanceView(View):
    template_name = "interview_q/send.html"
    def get(self, request, *args, **kwargs):
        question = None
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        return render(request, self.template_name, {'question': question})
    def post(self, request,  *args, **kwargs):
        user_email = self.request.POST.get('email', '')
        base_question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        if len(user_email) == 0:
            return render(request, self.template_name, {"error_message": "email field not filled out"})
        
        curr_time_zone = 'US/Eastern'
        num_hours = 4

        start_date_field_str = self.request.POST.get('start_date', '')
        start_date_field = datetime.strptime(start_date_field_str, "%Y-%m-%dT%H:%M") + timedelta(hours=num_hours)

        expire_date_field_str = self.request.POST.get('expiration_date', '')
        expire_date_field = datetime.strptime(expire_date_field_str, "%Y-%m-%dT%H:%M").astimezone(pytz.utc) + timedelta(hours=num_hours)

        question_instance = InterviewQuestionInstance(interviewee_email=user_email, base_question=base_question, start_time=start_date_field, expire_time=expire_date_field)
        question_instance.save()
        return HttpResponseRedirect("/interview_questions/")

class CreateOpenQuestionInstanceView(View):
    def get(self, request,  *args, **kwargs):
        user_email = self.request.user.email
        base_question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        # see if the user already attempted the question
        user_question_instance = InterviewQuestionInstance.objects.filter(base_question=base_question, interviewee_email=user_email)
        question_instance = None
        if len(user_question_instance) > 0:
            # already exists
            question_instance = user_question_instance[0]
        else:
            question_instance = InterviewQuestionInstance(interviewee_email=user_email, base_question=base_question, start_time=datetime.now())
            question_instance.save()
        return HttpResponseRedirect("/questions/answer/" + str(question_instance.id) + "/")

class ValidateQuestionView(View):
    template_name = "interview_q/validate.html"
    def get(self, request,  *args, **kwargs):
        question = None
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=kwargs['pk'])
            if request.user == question.creator:
                # create question instance
                question_instance = InterviewQuestionInstance(interviewee_email=request.user.email, base_question=question, start_time=datetime.now())
                question_instance.save()
                test_passed, test_results = create_and_run_submission(request, question, question_instance, True, '')
                return render(request, self.template_name, {'question': question, 'test_passed': test_passed, 'test_results': test_results})
        return render(request, "no_auth.html", {})
        