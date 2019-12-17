from django.core.management.base import BaseCommand
from users.models import SiteUser, SubscriptionCouponCode, Subscription
from interview_q.models import InterviewQuestion
from django.db.models import Q
from datetime import timedelta
from django.conf import settings 
from django.utils import timezone
import stripe

import datetime

class Command(BaseCommand):

    help = 'Resets Subscription if expired and disables questions by the user'

    def handle(self, *args, **kwargs):
        # get users more than 1 day expired
        stripe.api_key = settings.STRIPE_SECRET_KEY
        now = datetime.datetime.now(tz=timezone.utc)
        yesterday = now - timedelta(days=1)
        expired_subscription_users = SiteUser.objects.filter(~Q(subscription__plan_type = 'SHY'), Q(subscription__terminated_on__lt=yesterday))
        for expired_user in expired_subscription_users:
            # see if they did not pay see if the expire time of the subscription is before today
            has_subscirption = expired_user.stripe_subscription_id != None and len(expired_user.stripe_subscription_id) > 0
            if has_subscirption:
                subscription_obj = stripe.Subscription.retrieve(expired_user.stripe_subscription_id)

                no_stripe_subscription = "current_period_end" in subscription_obj
                subscription_expired = False

                if not no_stripe_subscription:
                    current_period_end = datetime.datetime.fromtimestamp(subscription_obj["current_period_end"])
                    subscription_expired = current_period_end < now
                    
                if subscription_expired or no_stripe_subscription:
                    # reset subscription
                    expired_user.subscription.plan_type = "SHY"
                    expired_user.subscription.save()
                    # disable questions
                    user_questions = InterviewQuestion.objects.filter(creator=expired_user)
                    for question in user_questions:
                        if not question.is_open:
                            question.is_disabled = True
                            question.save()
                

