from django.db import models

class Method(models.Model):
    body = models.TextField()
    interview_question_api = models.ForeignKey('api_q.InterviewAPI', on_delete=models.CASCADE)
