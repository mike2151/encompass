from django.db import models

class InterviewQuestion(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    creator = models.ForeignKey('users.SiteUser',on_delete=models.CASCADE)
    time_limit_minutes = models.IntegerField(default=60)
    language = models.CharField(max_length=128, default="Python3")
    api = models.ForeignKey('api_q.InterviewAPI', on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    id = models.AutoField(primary_key=True)
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return self.name
