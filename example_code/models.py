from django.db import models

class ExampleCode(models.Model):
    def upload_path_handler(self, instance, filename):
        return "code_files/example_code_files/{id}".format(id=instance.id)
    body = models.TextField(null=True)
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    
    code_file = models.FileField(upload_to=upload_path_handler, null=True)
