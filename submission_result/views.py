from django.views import View
from django.shortcuts import render
import json
from .models import SubmissionResult
from django.conf import settings
import os


class SubmissionView(View):
    # user's view
    template_name = "results/submission.html"
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            result = SubmissionResult.objects.get(pk=int(self.kwargs['pk']))
            if result.user == request.user:
                test_passed = json.loads(result.tests_passed_body)
                test_results = json.loads(result.results_body)
                test_visability = json.loads(result.visability_body)

                return_test_passed = {}
                return_test_results = {}

                for k,v in test_passed.items():
                    if test_visability[k]:
                        return_test_passed[k] = v
                        return_test_results[k] = test_results[k]

                return render(request, self.template_name, {'question': result.interview_question, 'test_passed': return_test_passed, 'test_results': return_test_results})
        return render(request, "no_auth.html", {})
class CreatorSubmissionResult(View):
    template_name = "results/creator_submission.html"
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            result = SubmissionResult.objects.get(pk=int(self.kwargs['pk']))
            if result.interview_question.creator == request.user:
                test_passed = json.loads(result.tests_passed_body)
                test_results = json.loads(result.results_body)

                # get the files
                file_contents = {}
                base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(result.interview_question.pk))
                instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(result.question_instance_pk))

                for subdir, dirs, files in os.walk(instance_question_dir):
                    for s_file in files:
                        file_content = open((os.path.join(instance_question_dir, s_file)), "r").read()
                        file_contents[str(s_file)] = file_content

                return render(request, self.template_name, {'question': result.interview_question, 'test_passed': test_passed, 'test_results': test_results, 'file_contents': file_contents})
            return render(request, "no_auth.html", {})