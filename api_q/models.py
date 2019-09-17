from django.db import models

class InterviewAPI(models.Model):
    description = models.TextField(null=True, blank=True)
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    

