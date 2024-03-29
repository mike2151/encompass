from django.views import View
from django.shortcuts import render
from .models import InterviewQuestionInstance
from method_signature.models import MethodSignature
from example_code.models import ExampleCode
from interview_code_file.models import SupportCode
from .util import create_and_run_submission
from django.http import HttpResponseRedirect
from submission_result.models import SubmissionResult
from starter_code.models import StarterCode
import json
from api_q.models import InterviewAPI
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse
import pytz
from django.utils.timezone import utc
from django.utils import timezone
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
import os


class AllQuestionsToAnswerView(View):
    template_name = "interview_q_instance/browse.html"
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, "no_auth.html", {})
        preview_questions = []
        available_questions = []
        completed_questions = []
        now = datetime.now().date()
        available_questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_completed=False, start_time__lt=now, expire_time__gt=now).order_by('-creation_time')
        preview_questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_completed=False, start_time__gte=now, expire_time__gt=now).order_by('-creation_time')
        completed_questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_completed=True).order_by('-creation_time')
        return render(request, self.template_name, {
            "available_questions": available_questions,
            "preview_questions": preview_questions,
            "completed_questions": completed_questions
            })

class UserTestCaseView(View):
    def post(self, request, *args, **kwargs):
        test_case_body = request.POST.get("test_case_editor", '').replace("\t", "    ")
        public_test_passed = {}
        public_test_results = {}
        if len(test_case_body) > 0:
            question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
            if (question_instance.base_question.is_open and question_instance.is_anon_user) or (question_instance.interviewee_email == request.user.email):
                test_passed, test_results, test_visability = create_and_run_submission(request, question_instance.base_question, question_instance, False, test_case_body)

                for k,v in test_passed.items():
                    if test_visability[k]:
                        public_test_passed[k] = v
                        public_test_results[k] = test_results[k]
        return JsonResponse({
            'test_passed': public_test_passed,
            'test_results': public_test_results
        })

class SaveCodeView(View):
    def post(self, request, *args, **kwargs):
        file_contents_json = request.POST.get("json_file_contents", '')
        new_files_contents_json = request.POST.get("new_files", '')
        successful_save = False
        if len(file_contents_json) > 0:
            question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
            if question_instance.interviewee_email == request.user.email:
                question_instance.current_working_body = file_contents_json
                if question_instance.base_question.allow_new_files:
                    question_instance.new_files_body = new_files_contents_json
                question_instance.save()
                successful_save = True
        return JsonResponse({
            'success': successful_save,
        })


class QuestionAnswerView(View):
    template_name = "interview_q_instance/answer.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
        if question.base_question.is_disabled:
            return render(request, "disabled_question.html", {})
        if (request.user.is_authenticated and question.interviewee_email == request.user.email) or (question.base_question.is_open and question.is_anon_user):
            if question.has_completed and (not question.base_question.is_open):
                return HttpResponseRedirect("/questions/answer")
            files_to_work_on = StarterCode.objects.filter(interview_question=question.base_question)

            api_methods = ""
            api = InterviewAPI.objects.filter(interview_question=question.base_question).first()
            api_description = ""
            if api is not None:
                api_description = api.description
                api_methods_objs = MethodSignature.objects.filter(interview_question_api=api)
                for api_method_obj in api_methods_objs:
                    api_methods = api_methods + str(api_method_obj.api_signature) + "<br><br>"

            files_to_work_on_names = []
            files_to_work_on_bodies = []

            previous_work = {}
            try:
                previous_work = json.loads(question.current_working_body)
            except:
                previous_work = {}

            for file_obj in files_to_work_on:
                filename = file_obj.code_file.name.split("/")[-1]
                if "wfile_" + filename in previous_work:
                    files_to_work_on_names.append(filename)
                    files_to_work_on_bodies.append(previous_work["wfile_" + filename])
                else:
                    files_to_work_on_names.append(filename)
                    f = file_obj.code_file
                    f.open(mode='r') 
                    content = f.read()
                    f.close()
                    files_to_work_on_bodies.append(content)

            new_files_names_to_bodies = {}
            if question.base_question.allow_new_files:
                previous_work = {}
                try:
                    previous_work = json.loads(question.new_files_body)
                except:
                    previous_work = {}

                for key, value in previous_work.items():
                    new_files_names_to_bodies[key] = value


            example_file_objs = ExampleCode.objects.filter(interview_question=question.base_question)
            example_files_names = []
            example_files_bodies = []
            for example_file_obj in example_file_objs:
                filename = example_file_obj.code_file.name.split("/")[-1]
                example_files_names.append(filename)
                f = example_file_obj.code_file
                f.open(mode='r') 
                content = f.read()
                f.close()
                example_files_bodies.append(content)

            is_preview = (question.start_time.date() > datetime.now().date()) and question.can_preview

            opt_groups = ["Question (Not Modifiable)", "Required Files (Modifiable)", "API (Not Modifiable)", "Example Code (Not Modifiable)", "Allowed Imports (Not Modifiable)"]
            if question.base_question.allow_new_files:
                opt_groups.insert(2, "New Files (Modifiable)")
            # see if there is api
            if len(api_description) == 0 and len(api_methods) == 0:
                opt_groups.remove("API (Not Modifiable)")
            # see if there is example files
            if len(example_files_names) == 0:
                opt_groups.remove("Example Code (Not Modifiable)")

            expiration_time_in_seconds = 0
            has_expiration = True

            if is_preview:
                has_expiration = False
                files_to_work_on_names = []
                files_to_work_on_bodies = []
            else:
                if not question.expire_time:
                    if question.how_many_minutes == 0:
                        has_expiration = False
                        if not question.has_started:
                            question.has_started = True
                            question.save()
                    else:
                        expiration_time_in_seconds = question.how_many_minutes * 60.0

                        question.expire_time = datetime.now() + timedelta(minutes=question.how_many_minutes)
                        
                        question.has_started = True
                        question.save()
                else:
                    utc = pytz.utc
                    now = datetime.now(tz=utc)
                    expire_time = question.expire_time
                    expiration_time_in_seconds = (expire_time - now).total_seconds()
                    question.has_started = True
                    question.save()

                # imports
                external_allowed_imports = str(question.base_question.dependencies).replace(",", "<br />")
                external_allowed_imports = "External Allowed Imports: <br><br /><code>" + external_allowed_imports + "</code>" if len(external_allowed_imports) > 0 else ""
                support_code_objs = SupportCode.objects.filter(interview_question=question.base_question)
                code_base_files = []
                for support_code_obj in support_code_objs:
                    if ".py" in support_code_obj.code_file.name:
                        code_base_files.append(support_code_obj.code_file.name.split("/")[-1].split(".")[0])
                code_base_files_str = ""
                for code_base_file in code_base_files:
                    code_base_files_str = code_base_files_str + "<br><code>" + code_base_file + "</code>"
                code_base_allowed = "Provided Code Base Files You Can Import:<br /> " + code_base_files_str + "<br><br>"
                if len(code_base_files) == 0:
                    code_base_allowed = ""
                allowed_imports = "<u><b>Allowed Imports:</b></u> <br><br>All Python standard libraries are allowed except for the ones detailed in the banned section.<br><br>" + code_base_allowed + external_allowed_imports

                not_allowed_imports = str(question.base_question.banned_imports).replace(",", "<br />")
                network_banned =  "<b>Note that this question has disabled network access so any network related code will fail.</b><br><br>" if not question.base_question.network_enabled else "" 
                not_allowed_imports = "<br /><u><b>Imports Not Allowed:</b></u> <br><br>" + network_banned + "<code>" + not_allowed_imports + "</code>" if len(not_allowed_imports) > 0 else ""
                if len(not_allowed_imports) == 0:
                    allowed_imports = allowed_imports.replace("except for the ones detailed in the banned section.", "")
                imports_body = allowed_imports + "<br />" + not_allowed_imports

            prepend_title = "## Question: " + question.base_question.name + "<br><br>\n Instructions: Please modify the required files or upload a zip file containing the required files and press the Submit Code button when finished.<br><br>\n"
            question_description = prepend_title + question.base_question.description
            return render(request, self.template_name, {
                'question': question,
                'network_enabled': question.base_question.network_enabled,
                'question_description': question_description,
                'api_methods': api_methods,
                'api_description': api_description,
                'example_files_bodies': json.dumps(example_files_bodies),
                'example_files_names': example_files_names,
                'files_to_work_on_bodies': json.dumps(files_to_work_on_bodies),
                'files_to_work_on_names': files_to_work_on_names,
                'new_files_names_to_bodies': new_files_names_to_bodies,
                'imports_body': imports_body,
                'is_preview': is_preview,
                "opt_groups": opt_groups,
                "expiration_time": expiration_time_in_seconds,
                'has_expiration': has_expiration,
                "live_interview_id": question.live_interview_id,
                "is_observer": False,
                "is_anon_user": question.is_anon_user,
                "is_open": question.base_question.is_open
                })
        return render(request, "no_auth.html", {})

    def post(self, request, *args, **kwargs):
        question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
        if question_instance.base_question.is_disabled:
            return render(request, "disabled_question.html", {})
        if question_instance.interviewee_email == request.user.email:
            has_expiration = (not question_instance.expire_time) and (question_instance.how_many_minutes != 0)
            if has_expiration:
                # check if maliciously manipulated
                utc = pytz.utc
                now = datetime.now(tz=utc)
                expire_time = question_instance.expire_time
                expiration_time_in_seconds = (now - expire_time).total_seconds()  

                if expiration_time_in_seconds < 35:
                    test_passed, test_results, test_visability = create_and_run_submission(request, question_instance.base_question, question_instance, False, '')

                    # pass results to results page
                    submission_result = SubmissionResult(
                        tests_passed_body=json.dumps(test_passed), 
                        results_body=json.dumps(test_results), 
                        visability_body=json.dumps(test_visability),
                        interview_question=question_instance.base_question, 
                        question_instance_pk=question_instance.pk,
                        user = request.user,
                        expire_time = datetime.now(timezone.utc) + timedelta(days=30)
                        )
                    submission_result.save()
                    question_instance.submission_result = submission_result
                    question_instance.has_completed = True
                    question_instance.save()
                    question_instance.delete_all_but_submission_files()

                    # email the creator
                    name_of_question = question_instance.base_question.name
                    name_of_user = request.user.first_name + request.user.last_name
                    results_url = get_current_site(request) + "/results/submissions/" + str(submission_result.pk)
                    if not question_instance.base_question.is_open and not question_instance.is_anon_user:
                        mail_subject = "An Interview Question Has Been Submitted"
                        message = "Hello ,\n\n {0} has submitted {1}. You can view the submission here: {2}. \n\n Best, \n The Encompass Team".format(name_of_user, name_of_question, results_url)
                        email_obj = EmailMessage(
                            mail_subject, message, to=[user_email]
                        )
                        email_obj.send()

                    return HttpResponseRedirect("/results/" + str(submission_result.id))
            else:
                test_passed, test_results, test_visability = create_and_run_submission(request, question_instance.base_question, question_instance, False, '')
                # pass results to results page
                submission_result = SubmissionResult(
                    tests_passed_body=json.dumps(test_passed), 
                    results_body=json.dumps(test_results), 
                    visability_body=json.dumps(test_visability),
                    interview_question=question_instance.base_question, 
                    question_instance_pk=question_instance.pk,
                    user = request.user, 
                    expire_time = datetime.now(timezone.utc) + timedelta(days=30)
                    )
                submission_result.save()
                question_instance.submission_result = submission_result
                question_instance.has_completed = True
                question_instance.save()
                question_instance.delete_all_but_submission_files()
            return HttpResponseRedirect("/results/" + str(submission_result.id))
        return HttpResponseRedirect("/questions/answer")

class QuestionObserveView(View):
    template_name = "interview_q_instance/answer.html"
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            question = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
            if question.base_question.is_disabled:
                return render(request, "disabled_question.html", {})
            if question.base_question.creator.email == request.user.email:
                if question.has_completed and (not question.base_question.is_open):
                    return HttpResponseRedirect("/questions/answer")
                files_to_work_on = StarterCode.objects.filter(interview_question=question.base_question)

                api_methods = ""
                api = InterviewAPI.objects.filter(interview_question=question.base_question).first()
                api_description  = ""
                if api is not None:
                    api_description = api.description
                    api_methods_objs = MethodSignature.objects.filter(interview_question_api=api)
                    for api_method_obj in api_methods_objs:
                        api_methods = api_methods + str(api_method_obj.api_signature) + "<br><br>"

                files_to_work_on_names = []
                files_to_work_on_bodies = []

                previous_work = {}
                try:
                    previous_work = json.loads(question.current_working_body)
                except:
                    previous_work = {}

                for file_obj in files_to_work_on:
                    filename = file_obj.code_file.name.split("/")[-1]
                    if "wfile_" + filename in previous_work:
                        files_to_work_on_names.append(filename)
                        files_to_work_on_bodies.append(previous_work["wfile_" + filename])
                    else:
                        files_to_work_on_names.append(filename)
                        f = file_obj.code_file
                        f.open(mode='r') 
                        content = f.read()
                        f.close()
                        files_to_work_on_bodies.append(content)

                new_files_names_to_bodies = {}
                if question.base_question.allow_new_files:
                    previous_work = {}
                    try:
                        previous_work = json.loads(question.new_files_body)
                    except:
                        previous_work = {}

                    for key, value in previous_work.items():
                        new_files_names_to_bodies[key] = value


                example_file_objs = ExampleCode.objects.filter(interview_question=question.base_question)
                example_files_names = []
                example_files_bodies = []
                for example_file_obj in example_file_objs:
                    filename = example_file_obj.code_file.name.split("/")[-1]
                    example_files_names.append(filename)
                    f = example_file_obj.code_file
                    f.open(mode='r') 
                    content = f.read()
                    f.close()
                    example_files_bodies.append(content)

                is_preview = (question.start_time.date() > datetime.now().date()) and question.can_preview

                opt_groups = ["Question (Not Modifiable)", "Required Files (Modifiable)", "API (Not Modifiable)", "Example Code (Not Modifiable)"]
                if question.base_question.allow_new_files:
                    opt_groups.insert(2, "New Files (Modifiable)")

                expiration_time_in_seconds = 0
                has_expiration = True

                if is_preview:
                    has_expiration = False
                    files_to_work_on_names = []
                    files_to_work_on_bodies = []
                else:
                    if not question.expire_time:
                        if question.how_many_minutes == 0:
                            has_expiration = False
                            if not question.has_started:
                                question.has_started = True
                                question.save()
                        else:
                            expiration_time_in_seconds = question.how_many_minutes * 60.0

                            question.expire_time = datetime.now() + timedelta(minutes=question.how_many_minutes)
                            
                            question.has_started = True
                            question.save()
                    else:
                        utc = pytz.utc
                        now = datetime.now(tz=utc)
                        expire_time = question.expire_time
                        expiration_time_in_seconds = (expire_time - now).total_seconds()
                        question.has_started = True
                        question.save()
                return render(request, self.template_name, {
                    'question': question,
                    'question_description': question.base_question.description,
                    'api_methods': api_methods,
                    'api_description': api_description,
                    'example_files_bodies': json.dumps(example_files_bodies),
                    'example_files_names': example_files_names,
                    'new_files_names_to_bodies': new_files_names_to_bodies,
                    'files_to_work_on_bodies': json.dumps(files_to_work_on_bodies),
                    'files_to_work_on_names': files_to_work_on_names,
                    'is_preview': is_preview,
                    "opt_groups": opt_groups,
                    "expiration_time": expiration_time_in_seconds,
                    'has_expiration': has_expiration,
                    "live_interview_id": question.live_interview_id,
                    "is_observer": True,
                    "is_anon_user": question.is_anon_user,
                    "is_open": question.base_question.is_open
                    })
        return render(request, "no_auth.html", {})
