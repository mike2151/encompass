from django.db import models

class MethodSignature(models.Model):
    api_signature = models.TextField(default="")
    interview_question_api = models.ForeignKey('api_q.InterviewAPI', on_delete=models.CASCADE)

    def __str__(self):
        return self.api_signature
