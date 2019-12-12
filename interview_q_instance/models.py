from django.db import models
from submission_result.models import SubmissionResult
from users.models import SiteUser
import os
from django.conf import settings
import shutil
import uuid
from random import randint
import shutil

def make_uuid():
   return str(uuid.uuid4()).replace("-", "_")

def make_pk():
    num_digits = 16
    range_start = 10**(num_digits-1)
    range_end = (10**num_digits)-1
    return randint(range_start, range_end)

class InterviewQuestionInstance(models.Model):
    base_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    submission_result = models.ForeignKey(SubmissionResult, on_delete=models.CASCADE, null=True)
    interviewee = models.ForeignKey(SiteUser, on_delete=models.CASCADE, null=True),
    is_anon_user = models.BooleanField(default=False)
    ip_addr = models.CharField(max_length=128, default="")
    interviewee_email = models.CharField(max_length=128)
    creator_email = models.CharField(max_length=128)
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
    new_files_body = models.TextField(null=True, blank=True)
    id = models.BigIntegerField(primary_key=True, default=make_pk)
    live_interview_id = models.CharField(
      editable=False, max_length=36, default=make_uuid
    )


    def __str__(self):
        return self.interviewee_email + ":" + self.base_question.name

    def delete_folder(self):
        base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(self.base_question.pk))
        instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(self.pk))
        if os.path.exists(instance_question_dir):
            shutil.rmtree(instance_question_dir)

    def delete_all_but_submission_files(self):
        base_question_dir = os.path.join(settings.MEDIA_ROOT, '{0}'.format(self.base_question.pk))
        instance_question_dir = os.path.join(base_question_dir, 'instances/{0}'.format(self.pk))
        
        # delete user test folder if exists
        user_test_cases_dir = os.path.join(instance_question_dir, "user_test_cases")
        if os.path.exists(user_test_cases_dir):
            shutil.rmtree(user_test_cases_dir) 
        
        files_to_delete = ["__init__.py", "runner.py"]

        working_dir = os.path.join(base_question_dir, 'example_code_files')
        for subdir, dirs, files in os.walk(working_dir):
            for s_file in files:
                files_to_delete.append(str(s_file))

        working_dir = os.path.join(base_question_dir, 'supporting_code_files')
        for subdir, dirs, files in os.walk(working_dir):
            for s_file in files:
                files_to_delete.append(str(s_file))

        working_dir = os.path.join(base_question_dir, 'test_code_files')
        for subdir, dirs, files in os.walk(working_dir):
            for s_file in files:
                files_to_delete.append(str(s_file))

        for subdir, dirs, files in os.walk(instance_question_dir):
            for i_file in files:
                if i_file in files_to_delete or str(i_file).endswith(".pye"):
                    p = os.path.join(instance_question_dir, i_file)
                    if os.path.exists(p):
                        os.remove(p)