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
from django.core.paginator import Paginator
from submission_result.models import SubmissionResult
from dateutil import parser
import pytz
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site


class CreateInterviewView(View):
    def check_condition(self, request, name, number):
        cond_one = (len(request.POST.get(name + "_body_name_" + str(number), '')) > 0 and len(request.POST.get(name + "_body_" + str(number), '')) > 0)
        cond_two = request.FILES.get(name + "_file_" + str(number), False)
        return cond_one or cond_two

    template_name = 'interview_q/create.html'
    def get(self, request, *args, **kwargs):
        if request.user.subscription.plan_type != 'FREE':
            return render(request, self.template_name, {})
        else:
            return render(request, "no_auth.html", {})
    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated and request.user.subscription.plan_type != 'FREE':
            name = self.request.POST.get('name', '')
            description = self.request.POST.get('description', '')
            network_enabled = self.request.POST.get('network_enabled', '') == 'on'
            allow_stdout = self.request.POST.get('allow_stdout', '') == 'on'
            question_language = self.request.POST.get('question_language', '')
            if len(name) == 0:
                return render(request, self.template_name, {"error_message": "name field not filled out"})
            if len(description) == 0:
                return render(request, self.template_name, {"error_message": "description field not filled out"})
            question = InterviewQuestion(name=name, description=description, creator=self.request.user, language=question_language, network_enabled=network_enabled, allow_stdout=allow_stdout)
            if request.FILES.get("requirements_file", False):
                question.dependency_file = request.FILES["requirements_file"]
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
            can_user_make_questions = request.user.subscription.plan_type != 'FREE'
            return render(request, self.template_name, {
                'interview_questions': questions,
                'can_user_make_questions': can_user_make_questions})
        else:
            return render(request, "no_auth.html", {})

class DeleteQuestionView(View):
    template_name = 'interview_q/delete.html'
    def get(self, request, *args, **kwargs):
        question = None
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
            if question.creator == request.user:
                return render(request, self.template_name, {'question': question})
        return render(request, "no_auth.html", {})
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
        if (not request.user.subscription) or request.user.subscription.plan_type == 'FREE':
            return render(request, "no_auth.html", {})            
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        if question.creator != request.user:
            return render(request, "no_auth.html", {})

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
        if request.user.is_authenticated and request.user.subscription.plan_type != 'FREE':
            name = self.request.POST.get('name', '')
            description = self.request.POST.get('description', '')
            question_language = self.request.POST.get('question_language', '')
            network_enabled = self.request.POST.get('network_enabled', '') == 'on'
            allow_stdout = self.request.POST.get('allow_stdout', '') == 'on'
            if len(name) == 0:
                return render(request, self.template_name, {"error_message": "name field not filled out"})
            if len(description) == 0:
                return render(request, self.template_name, {"error_message": "description field not filled out"})
            question_id = kwargs['pk']
            question = InterviewQuestion.objects.get(pk=question_id)
            if question.creator != request.user:
                return HttpResponseRedirect("/interview_questions/")
            
            # replace basic fields
            question.name = name
            question.description = description
            question.language = question_language
            question.network_enabled = network_enabled
            question.allow_stdout = allow_stdout

            if request.FILES.get("requirements_file", False):
                question.dependency_file = request.FILES["requirements_file"]

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

class CreateQuestionInstanceView(View):
    template_name = "interview_q/send.html"
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.subscription.plan_type != 'FREE':
                question = InterviewQuestion.objects.get(pk=kwargs['pk'])
                if question.creator == request.user:
                    return render(request, self.template_name, {'question': question})
        return render(request, "no_auth.html", {})
    def post(self, request,  *args, **kwargs):
        if (not request.user.is_authenticated) or (not request.user.subscription.plan_type != 'FREE'):
            return HttpResponseRedirect("/interview_questions/")
        user_email = self.request.POST.get('email', '')
        base_question = InterviewQuestion.objects.get(pk=kwargs['pk'])
        if base_question.creator != request.user:
            return HttpResponseRedirect("/interview_questions/")
        if len(user_email) == 0:
            return render(request, self.template_name, {"error_message": "email field not filled out"})

        start_date_field_str = self.request.POST.get('start_date', '')

        start_time_zone_str = self.request.POST.get('start_time_tz', "-05:00")

        start_date_field = parser.parse(start_date_field_str + " " + start_time_zone_str)

        start_time_date_str = start_date_field.strftime("%b %d %Y %H:%M %p")

        can_preview = request.POST.get('preview_option', '') == 'on'

        is_minutes_option = request.POST.get('minutes_option', '') == 'on'
        if is_minutes_option:
            num_minutes = int(self.request.POST.get('how_many_minutes', '60'))
            num_minutes = max(num_minutes, 1)
            question_instance = InterviewQuestionInstance(interviewee_email = user_email, creator_email = base_question.creator.email, base_question=base_question, start_time=start_date_field, is_minutes_expiration=True, how_many_minutes=num_minutes, start_time_date_str=start_time_date_str, can_preview=can_preview)
            question_instance.save()

            name_of_question = question_instance.base_question.name
            question_url = get_current_site(request) + "/questions/answer/" + str(question_instance.pk)
            mail_subject = "An Interview Question Has Been Sent To You"
            message = "Hello ,\n You have been asked to complete the following interview question: {0}. You can complete it by navigating here: {1}. \n Best of luck! \n The Encompass Team.".format(name_of_question, question_url)
            email_obj = EmailMessage(
                mail_subject, message, to=[user_email]
            )
            email_obj.send()
        else:
            expire_date_field_str = self.request.POST.get('expiration_date', '')
            expire_date_field = parser.parse(expire_date_field_str + " " + start_time_zone_str)
            question_instance = InterviewQuestionInstance(interviewee_email=user_email, creator_email = base_question.creator.email, base_question=base_question, start_time=start_date_field, expire_time=expire_date_field, start_time_date_str=start_time_date_str, can_preview=can_preview)
            question_instance.save()
        return HttpResponseRedirect("/interview_questions/")

class CreateOpenQuestionInstanceView(View):
    def get(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            user_email = self.request.user.email
            base_question = InterviewQuestion.objects.get(pk=kwargs['pk'])
            # see if the user already attempted the question
            user_question_instance = InterviewQuestionInstance.objects.filter(base_question=base_question, interviewee_email=user_email, creator_email = base_question.creator.email,)
            question_instance = None
            if len(user_question_instance) > 0:
                # already exists
                if user_question_instance[0].has_completed:
                    user_question_instance[0].delete_folder()
                    user_question_instance[0].delete()
                    question_instance = InterviewQuestionInstance(interviewee_email=user_email, base_question=base_question, creator_email = base_question.creator.email, start_time=datetime.now())
                    question_instance.save()
                else:    
                    question_instance = user_question_instance[0]
            else:
                question_instance = InterviewQuestionInstance(interviewee_email=user_email, base_question=base_question, creator_email = base_question.creator.email,  start_time=datetime.now())
                question_instance.save()
            return HttpResponseRedirect("/questions/answer/" + str(question_instance.id) + "/")
        else:
             return HttpResponseRedirect("/users/signup/")


class ValidateQuestionView(View):
    template_name = "interview_q/validate.html"
    def get(self, request,  *args, **kwargs):
        question = None
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=kwargs['pk'])
            if request.user == question.creator:
                # create question instance
                question_instance = InterviewQuestionInstance(interviewee_email=request.user.email, base_question=question, creator_email = question.creator.email, start_time=datetime.now())
                question_instance.save()
                test_passed, test_results, test_visability = create_and_run_submission(request, question, question_instance, True, '')
                question_instance.delete_folder()
                question_instance.delete()
                return render(request, self.template_name, {'question': question, 'test_passed': test_passed, 'test_results': test_results})
        return render(request, "no_auth.html", {})

class OpenQuestionView(View):
    template_name = "interview_q/open.html"
    def get(self, request,  *args, **kwargs):
        if request.user.is_authenticated:

            num_results_per_page = 30

            page = int(request.GET.get('page', 1))
            paginator = Paginator(InterviewQuestion.objects.filter(is_open=True), num_results_per_page)
            start_count = (page- 1) * num_results_per_page

            try:
                questions = paginator.page(page)
            except PageNotAnInteger:
                questions = paginator.page(1)
            except EmptyPage:
                questions = paginator.page(paginator.num_pages)

            return render(request, self.template_name, { 
                'questions': questions,
                'start_count': start_count 
                })
        return HttpResponseRedirect("/users/signup")

class SubmissionsQuestionView(View):
    template_name = "interview_q/submissions.html"
    def get(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            question = InterviewQuestion.objects.get(pk=kwargs['pk'])
            if question.creator == request.user:
                submissions = SubmissionResult.objects.filter(interview_question=question)
                return render(request, self.template_name, {'submissions': submissions, "question": question})
        return render(request, "no_auth.html", {})
