from django.conf import settings
import shutil
import os
from django.db import models


class SubmissionResult(models.Model):
    tests_passed_body = models.TextField(default='')
    results_body = models.TextField(default='')
    visability_body = models.TextField(default='')
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    
    expire_time = models.DateTimeField(null=True)
    question_instance_pk = models.IntegerField()
    submission_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.SiteUser', on_delete=models.CASCADE)   

    def delete_folder(self):
        base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(self.interview_question.pk))
        instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(self.question_instance_pk))
        shutil.rmtree(instance_question_dir)
