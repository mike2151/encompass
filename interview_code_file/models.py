from django.db import models

class InterviewCodeFile(models.Model):
    def upload_path_handler(self, instance, filename):
        return "code_files/supporting_code_files/{id}".format(id=instance.id)
    name = models.CharField(max_length=128, null=True)
    body = models.TextField(default="")
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)
    code_file = models.FileField(upload_to=upload_path_handler, null=True)
