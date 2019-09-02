from django.db import models

class InterviewQuestion(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    creator = models.ForeignKey('users.SiteUser',on_delete=models.CASCADE)
    time_limit_minutes = models.IntegerField(default=60)

    api = models.ForeignKey('api_q.InterviewAPI', on_delete=models.SET_NULL, null=True)


    id = models.AutoField(primary_key=True)
