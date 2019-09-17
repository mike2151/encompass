from django.views import View
from django.shortcuts import render
import json
from .models import SubmissionResult
class SubmissionView(View):
    template_name = "results/submission.html"
    def get(self, request, *args, **kwargs):
        result = SubmissionResult.objects.get(pk=int(self.kwargs['pk']))
        test_passed = json.loads(result.tests_passed_body)
        test_results = json.loads(result.results_body)
        return render(request, self.template_name, {'question': result.interview_question, 'test_passed': test_passed, 'test_results': test_results})
