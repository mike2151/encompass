from django.core.management.base import BaseCommand
from users.models import SiteUser, SubscriptionCouponCode, Subscription
from interview_q.models import InterviewQuestion
from django.db.models import Q

import datetime

class Command(BaseCommand):

    help = 'Resets Subscription if expired and disables questions by the user'

    def handle(self, *args, **kwargs):
        expired_subscription_users = SiteUser.objects.filter(~Q(subscription__plan_type = 'SHY'), Q(subscription__terminated_on__lt=datetime.datetime.now()))
        for expired_user in expired_subscription_users:
            # reset subscription
            expired_user.subscription.plan_type = "SHY"
            expired_user.subscription.save()
            # disable questions
            user_questions = InterviewQuestion.objects.filter(creator=expired_user)
            for question in user_questions:
                question.is_disabled = True
                question.save()
            

