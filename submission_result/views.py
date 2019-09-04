from django.views import View
from django.shortcuts import render
from .models import SubmissionResult
class SubmissionView(View):
    template_name = "results/submission.html"
    def get(self, request, *args, **kwargs):
        result = SubmissionResult.objects.get(pk=int(self.kwargs['pk']))
        return render(request, self.template_name, {"result": result})
