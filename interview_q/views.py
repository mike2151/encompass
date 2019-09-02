from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from .forms import InterviewQuestionCreationForm
from .models import InterviewQuestion
from django.views import View

class CreateInterviewView(CreateView):
    form_class = InterviewQuestionCreationForm
    success_url = reverse_lazy('')
    template_name = 'interview_q/create.html'

class HomeInterviewView(ListView):
    model = InterviewQuestion
    template_name = 'interview_q/all.html'
    context_object_name = 'interview_questions'        

    def get_queryset(self):
        return InterviewQuestion.objects.all()


class IndividualQuestionView(View):
    template_name = "interview_q/question.html"
    def get(self, request, *args, **kwargs):
        question = InterviewQuestion.objects.get(pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'question': question})
