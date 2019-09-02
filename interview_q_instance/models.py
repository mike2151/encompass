from django.db import models

class InterviewQuestionInstance(models.Model):
    base_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    interviewee_email = models.CharField(max_length=128)
    submission = models.TextField(blank=True, null=True)
    has_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True)
    