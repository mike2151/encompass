from django.db import models

class SubmissionResult(models.Model):
    passed = models.BooleanField(default=False)
