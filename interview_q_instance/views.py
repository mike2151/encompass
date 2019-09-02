from django.views import View
from django.shortcuts import render
from .models import InterviewQuestionInstance

class AllQuestionsToAnswerView(View):
    template_name = "interview_q_instance/browse.html"
    def get(self, request, *args, **kwargs):
        questions = InterviewQuestionInstance.objects.filter(interviewee_email=request.user.email, has_started=False).order_by('-creation_time')
        return render(request, self.template_name, {"questions": questions})


class QuestionAnswerView(View):
    template_name = "interview_q_instance/answer.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestionInstance.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'question': question})