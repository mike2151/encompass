from django.db import models
from django.contrib.auth.models import AbstractUser

class SiteUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=64,
        unique=True,
    )

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)

    is_interview_creator = models.BooleanField(default=False)
    company = models.CharField(max_length=256, null=True, blank=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__ (self):
        return self.email


