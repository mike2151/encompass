from django.db import models
from submission_result.models import SubmissionResult

class InterviewQuestionInstance(models.Model):
    base_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    submission_result = models.ForeignKey(SubmissionResult, on_delete=models.CASCADE, null=True)
    interviewee_email = models.CharField(max_length=128)
    submission = models.TextField(blank=True, null=True)
    has_completed = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True)
    is_minutes_expiration = models.BooleanField(default=False)
    how_many_minutes = models.IntegerField(default=0)
    expire_time = models.DateTimeField(null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    start_time_date_str = models.CharField(null=True, blank=True, max_length=256)

    def __str__(self):
        return self.interviewee_email + ":" + self.base_question.name
    