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


class AllQuestionsToAnswerView(View):
    template_name = "interview_q_instance/browse.html"
    def get(self, request, *args, **kwargs):
        questions = []
        if request.user.is_authenticated:
            now = datetime.now().date()
            available_questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_completed=False, start_time__lt=now).order_by('-creation_time')
            preview_questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_completed=False, start_time__gte=now).order_by('-creation_time')
        return render(request, self.template_name, {
            "available_questions": available_questions,
            "preview_questions": preview_questions
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

        if is_preview:
            return render(request, self.template_name, {
                'question': question,
                'api_methods': api_methods,
                'example_code_snippets': [],
                'files_to_work_on_bodies': [],
                'files_to_work_on_names': [],
                'is_preview': is_preview
                })
        else:
            return render(request, self.template_name, {
                'question': question,
                'api_methods': api_methods,
                'example_code_snippets': [],
                'files_to_work_on_bodies': json.dumps(files_to_work_on_bodies),
                'files_to_work_on_names': files_to_work_on_names,
                'is_preview': is_preview
                })

    def post(self, request, *args, **kwargs):
        if request.POST['action'] == 'submit_code':
            question_instance = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))

            test_passed, test_results = create_and_run_submission(request, question_instance.base_question, question_instance, False)
            
            test_results_json = json.dumps(test_results)
            test_passed_json = json.dumps(test_passed)

            # pass results to results page
            submission_result = SubmissionResult(tests_passed_body=test_passed_json, results_body=test_results_json, interview_question=question_instance.base_question)
            submission_result.save()
            question_instance.submission_result = submission_result
            question_instance.save()
            return HttpResponseRedirect("/results/" + str(submission_result.id))
            