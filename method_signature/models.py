from django.db import models

class Method(models.Model):
    name = models.CharField(max_length=256)
    body = models.TextField()
