from django.contrib import admin
from .models import SiteUser, Subscription, SubscriptionCouponCode

admin.site.register(SiteUser)
admin.site.register(Subscription)
admin.site.register(SubscriptionCouponCode)
