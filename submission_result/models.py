from django.db import models

class SubmissionResult(models.Model):
    tests_passed_body = models.TextField(default='')
    results_body = models.TextField(default='')
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    
