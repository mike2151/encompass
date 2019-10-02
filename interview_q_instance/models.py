from django.db import models
from submission_result.models import SubmissionResult
import os
from django.conf import settings
import shutil

class InterviewQuestionInstance(models.Model):
    base_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    submission_result = models.ForeignKey(SubmissionResult, on_delete=models.CASCADE, null=True)
    interviewee_email = models.CharField(max_length=128)
    has_completed = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True)
    is_minutes_expiration = models.BooleanField(default=False)
    how_many_minutes = models.IntegerField(default=0)
    expire_time = models.DateTimeField(null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    start_time_date_str = models.CharField(null=True, blank=True, max_length=256)
    can_preview = models.BooleanField(default=False)
    current_working_body = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.interviewee_email + ":" + self.base_question.name

    def delete_folder(self):
        base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(self.base_question.pk))
        instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(self.pk))
        shutil.rmtree(instance_question_dir)

    def delete_all_but_submission_files(self):
        base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(self.base_question.pk))
        
        starter_dir = os.path.join(base_question_dir, 'starter_code_files')
        instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(self.pk))

        starter_files = []
        for subdir, dirs, files in os.walk(starter_dir):
            for s_file in files:
                starter_files.append(str(s_file))

        for subdir, dirs, files in os.walk(instance_question_dir):
            for i_file in files:
                if not (str(i_file) in starter_files):
                    os.remove(os.path.join(instance_question_dir, i_file))