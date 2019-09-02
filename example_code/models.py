from django.db import models

class ExampleCode(models.Model):
    body = models.TextField()
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    

