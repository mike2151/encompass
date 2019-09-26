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
from datetime import datetime
from django.http import JsonResponse
import pytz
from django.utils.timezone import utc
from django.utils import timezone


class AllQuestionsToAnswerView(View):
    template_name = "interview_q_instance/browse.html"
    def get(self, request, *args, **kwargs):
        preview_questions = []
        available_questions = []
        completed_questions = []
        if request.user.is_authenticated:
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

        is_preview = question.start_time.date() > datetime.now().date()

        opt_groups = ["Question", "Stub Files", "API", "Example Code"]

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
                expiration_time_in_seconds = question.how_many_minutes * 60.0

                num_hours = 4
                question.expire_time = datetime.now() + timedelta(hours=num_hours)
                
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
                "expiration_time": expiration_time_in_seconds
                })

    def post(self, request, *args, **kwargs):
        question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))

        # check if maliciously manipulated
        now = datetime.now().replace(tzinfo=utc)
        expire_time = question_instance.expire_time
        expiration_time_in_seconds = (now - expire_time).total_seconds()

        if expiration_time_in_seconds < 35:
            test_passed, test_results = create_and_run_submission(request, question_instance.base_question, question_instance, False, '')
            
            test_results_json = json.dumps(test_results)
            test_passed_json = json.dumps(test_passed)

            # pass results to results page
            submission_result = SubmissionResult(tests_passed_body=test_passed_json, results_body=test_results_json, interview_question=question_instance.base_question)
            submission_result.save()
            question_instance.submission_result = submission_result
            question_instance.has_completed = True
            question_instance.save()
            return HttpResponseRedirect("/results/" + str(submission_result.id))
        else:
            return HttpResponseRedirect("/questions/answer")

class UserTestCaseView(View):
    def post(self, request, *args, **kwargs):
        test_case_body = request.POST.get("test_case_editor", '')
        test_passed = {}
        test_results = {}
        if len(test_case_body) > 0:
            question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
            test_passed, test_results = create_and_run_submission(request, question_instance.base_question, question_instance, False, test_case_body)
        return JsonResponse({
            'test_passed': test_passed,
            'test_results': test_results
        })