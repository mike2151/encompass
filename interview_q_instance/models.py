from django.db import models

class InterviewQuestionInstance(models.Model):
    base_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    interviewee_email = models.CharField(max_length=128)
    submission = models.TextField(blank=True, null=True)
    has_completed = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.interviewee_email + ":" + self.base_question.name
    