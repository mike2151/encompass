from django.db import models

class InterviewQuestion(models.Model):
    def upload_path_handler(question, filename):
        return "{id}/dependency/{file}".format(id=question.pk, file=filename)

    name = models.CharField(max_length=128)
    description = models.TextField()
    creator = models.ForeignKey('users.SiteUser',on_delete=models.CASCADE)
    time_limit_minutes = models.IntegerField(default=60)
    language = models.CharField(max_length=128, default="Python3")
    network_enabled = models.BooleanField(default=False)
    allow_stdout = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    dependency_file = models.FileField(upload_to=upload_path_handler, null=True)
    banned_imports = models.TextField()

    id = models.AutoField(primary_key=True)
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return self.name
