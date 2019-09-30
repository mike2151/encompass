from django.db import models

class SubmissionResult(models.Model):
    tests_passed_body = models.TextField(default='')
    results_body = models.TextField(default='')
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    
    expire_time = models.DateTimeField(null=True)
    question_instance_pk = models.IntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.SiteUser', on_delete=models.CASCADE)    
