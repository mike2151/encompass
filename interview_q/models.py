from django.db import models
from random import randint

def make_uuid():
    pass

def make_pk():
    num_digits = 16
    range_start = 10**(num_digits-1)
    range_end = (10**num_digits)-1
    return randint(range_start, range_end)
    

class InterviewQuestion(models.Model):
    def upload_path_handler(question, filename):
        pass

    name = models.CharField(max_length=128)
    description = models.TextField()
    creator = models.ForeignKey('users.SiteUser',on_delete=models.CASCADE)
    time_limit_minutes = models.IntegerField(default=60)
    language = models.CharField(max_length=128, default="Python3")
    network_enabled = models.BooleanField(default=False)
    allow_stdout = models.BooleanField(default=False)
    allow_new_files = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    dependencies = models.TextField()
    banned_imports = models.TextField()

    id = models.IntegerField(primary_key=True, default=make_pk)
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return self.name
