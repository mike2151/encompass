from django.views import View
from django.shortcuts import render
from .models import InterviewQuestionInstance
from method_signature.models import MethodSignature
from example_code.models import ExampleCode
from .util import create_and_run_submission
from django.http import HttpResponseRedirect
from submission_result.models import SubmissionResult
from starter_code.models import StarterCode
import json
from api_q.models import InterviewAPI
from datetime import datetime, timedelta
from django.http import JsonResponse
import pytz
from django.utils.timezone import utc
from django.utils import timezone


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


class QuestionAnswerView(View):
    template_name = "interview_q_instance/answer.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
        if question.interviewee_email == request.user.email:
            files_to_work_on = StarterCode.objects.filter(interview_question=question.base_question)

            api_methods = []
            api = InterviewAPI.objects.filter(interview_question=question.base_question).first()
            if api is not None:
                api_methods = MethodSignature.objects.filter(interview_question_api=api)

            files_to_work_on_names = []
            files_to_work_on_bodies = []
            for file_obj in files_to_work_on:
                filename = file_obj.code_file.name.split("/")[-1]
                files_to_work_on_names.append(filename)
                f = file_obj.code_file
                f.open(mode='r') 
                content = f.read()
                f.close()
                files_to_work_on_bodies.append(content)

            is_preview = (question.start_time.date() > datetime.now().date()) and question.can_preview

            opt_groups = ["Question", "Stub Files", "API", "Example Code"]

            expiration_time_in_seconds = 0
            has_expiration = True

            if is_preview:
                return render(request, self.template_name, {
                    'question': question,
                    'question_description': json.dumps(question.base_question.description),
                    'api_methods': api_methods,
                    'example_code_snippets': [],
                    'files_to_work_on_bodies': [],
                    'files_to_work_on_names': [],
                    'is_preview': is_preview,
                    "opt_groups": opt_groups,
                    })
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
                    'question_description': json.dumps(question.base_question.description),
                    'api_methods': api_methods,
                    'example_code_snippets': [],
                    'files_to_work_on_bodies': json.dumps(files_to_work_on_bodies),
                    'files_to_work_on_names': files_to_work_on_names,
                    'is_preview': is_preview,
                    "opt_groups": opt_groups,
                    "expiration_time": expiration_time_in_seconds,
                    'has_expiration': has_expiration
                    })
        return render(request, "no_auth.html", {})

    def post(self, request, *args, **kwargs):
        question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
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
                        user = request.user
                        )
                    submission_result.save()
                    question_instance.submission_result = submission_result
                    question_instance.has_completed = True
                    question_instance.save()
                    question_instance.delete_all_but_submission_files()
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
                    user = request.user
                    )
                submission_result.save()
                question_instance.submission_result = submission_result
                question_instance.has_completed = True
                question_instance.save()
                question_instance.delete_all_but_submission_files()
            return HttpResponseRedirect("/results/" + str(submission_result.id))
        return HttpResponseRedirect("/questions/answer")

class UserTestCaseView(View):
    def post(self, request, *args, **kwargs):
        test_case_body = request.POST.get("test_case_editor", '')
        public_test_passed = {}
        public_test_results = {}
        if len(test_case_body) > 0:
            question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
            if question_instance.interviewee_email == request.user.email:
                test_passed, test_results, test_visability = create_and_run_submission(request, question_instance.base_question, question_instance, False, test_case_body)

                for k,v in test_passed.items():
                    if test_visability[k]:
                        public_test_passed[k] = v
                        public_test_results[k] = test_results[k]
        return JsonResponse({
            'test_passed': public_test_passed,
            'test_results': public_test_results
        })