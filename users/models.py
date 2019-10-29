from django.db import models
from django.contrib.auth.models import AbstractUser
from .plans import get_plan_names, get_max_questions

class SiteUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=64,
        unique=True,
    )

    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    is_from_company = models.BooleanField(default=False)
    company_org = models.CharField(max_length=256, null=True, blank=True)
    user_role = models.CharField(max_length=256, null=True, blank=True)

    subscription = models.ForeignKey('Subscription', on_delete=models.SET_NULL, null=True)

    num_questions_made = models.IntegerField(default=0)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

# SUBSCRIPTIONS:
class Subscription(models.Model):
    plans = get_plan_names()
    # stripe_subscription_id = models.CharField(max_length=100, primary_key=True)
    # stripe_customer_id = models.ForeignKey('Customer', db_column='stripe_customer_id', on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=35, choices=plans, default='SHY')
    initiated_on = models.DateTimeField(null=True, blank=True)
    terminated_on = models.DateTimeField(null=True, blank=True)
    coupon = models.ForeignKey('SubscriptionCouponCode', on_delete=models.SET_NULL, null=True)

    def get_max_num_questions(self):
        return get_max_questions(self.plan_type)

    def __str__(self):
        return self.plan_type


class SubscriptionCouponCode(models.Model):
    code = models.CharField(max_length=64)
    expiration_date = models.DateTimeField()
    description = models.CharField(max_length=512, null=True, blank=True)
    max_redeems = models.IntegerField(default=1)
    curr_redeems = models.IntegerField(default=0)
    def __str__(self):
        return self.code