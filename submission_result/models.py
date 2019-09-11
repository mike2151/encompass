from django.db import models

class SubmissionResult(models.Model):
    all_tests_passed = models.BooleanField(default=False)
    results_body = models.TextField(default='')
