from django.db import models

class InterviewAPI(models.Model):
    description = models.TextField(null=True, blank=True)
    

