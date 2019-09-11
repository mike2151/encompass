from django.db import models

class ExampleCode(models.Model):
    def upload_path_handler(instance, filename):
        return "example_code_files/{id}/{file}".format(id=instance.interview_question.pk, file=filename)
    interview_question = models.ForeignKey('interview_q.InterviewQuestion', on_delete=models.CASCADE)    
    code_file = models.FileField(upload_to=upload_path_handler, null=True)
