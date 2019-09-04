from django.db import models

class InterviewCodeFile(models.Model):
    body = models.TextField(default="")
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
