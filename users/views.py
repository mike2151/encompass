# users/views.py
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import SiteUser, Subscription, SubscriptionCouponCode
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from datetime import datetime, timedelta, timezone
from .plans import get_paid_plans, get_plan_by_price, get_max_questions
from django.conf import settings 
import math
from interview_q.models import InterviewQuestion

import stripe


class SignUpView(View):
    template_name = 'registration/signup.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        else:
            return render(request, self.template_name, {})
    def post(self, request,  *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        password2 = self.request.POST.get('password2', '')
        first_name = self.request.POST.get('first_name', '')
        last_name = self.request.POST.get('last_name', '')

        error_messages = []
        if len(first_name) == 0:
            error_messages.append("No first name given")

        if len(last_name) == 0:
            error_messages.append("No last name given")

        if password != password2:
            error_messages.append("passwords do not match")

        if len(password) < 8:
            error_messages.append("password length must be at least 8 characters")

        email_taken = True
        try:
            curr_user = SiteUser.objects.get(email=email)
            if curr_user is not None:
                if not curr_user.is_active:
                    email_taken = False
                    curr_user.delete()
        except SiteUser.DoesNotExist:
            email_taken = False

        if email_taken:
            error_messages.append("email taken")
        
        if len(error_messages) > 0:
            return render(request, self.template_name, {"error_messages": error_messages})

        is_from_company = request.POST.get('is_from_company', '') == 'on'
        subscription = Subscription()
        subscription.save()
        if is_from_company:
            company_org = request.POST.get('comp_org', '')
            if len(company_org) == 0:
                error_messages.append("No company/organization specified")
                return render(request, self.template_name, {"error_messages": error_messages})
            user = SiteUser.objects.create_user(username=email, email=email, password=password, company_org=company_org, is_from_company=True, first_name=first_name, last_name=last_name, is_active=False, subscription=subscription)
        else:
            user_role = request.POST.get('user_role', '')
            user = SiteUser.objects.create_user(username=email, email=email, password=password, user_role=user_role, first_name=first_name, last_name=last_name, is_active=False, subscription=subscription)
       
        current_site = get_current_site(request)
        mail_subject = 'Please Confirm Your Email For Encompass Interviews'
        message = render_to_string('registration/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        email_obj = EmailMessage(
            mail_subject, message, to=[email]
        )
        email_obj.send()
        return HttpResponseRedirect("/users/login/?status=confirm")

class LoginView(View):
    template_name = 'registration/login.html'   
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        else:
            message_to_render = ''
            message_color = "red"
            message = str(request.GET.get('status', ''))
            if message == "activated":
                message_to_render = "Your account is now activated. Please log in to proceed."
            elif message == "invalid_activation":
                message_to_render = "The account activation link does not exist or has expired. Please try signing up again."
                message_color = "green"
            elif message == "confirm":
                message_to_render = "Please check and confirm your email to proceed. You may need to check spam."

            return render(request, self.template_name, {"message": message_to_render, "message_color": message_color})
    def post(self, request,  *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        user = authenticate(request=request, username=email, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if user.is_from_company:
                    return HttpResponseRedirect("/interview_questions")
                else:
                    return HttpResponseRedirect("/questions/answer")
        return render(request, self.template_name, {"message": "Invalid email/password combination", "message_color": "red"})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = SiteUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, SiteUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect("/users/login/?status=activated")
    else:
        return HttpResponseRedirect("/users/login/?status=invalid_activation")

class EnrollView(View):
    def reactivate_questions(self, user):
        num_questions_reactivate = get_max_questions(user.subscription.plan_type)
        user_questions = InterviewQuestion.objects.filter(creator=user)[:num_questions_reactivate]
        if len(user_questions) > 0:
            for user_question in user_questions:
                user_question.is_disabled = False
                user_question.save()
        
    template_name = 'registration/enroll.html'   
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            plans = get_paid_plans()
            col_length = math.floor(12.0 / len(plans))
            is_active_member = request.user.is_authenticated and request.user.subscription.plan_type != 'SHY' and request.user.subscription.terminated_on > datetime.now(timezone.utc)
            return render(request, self.template_name, {
                "plans": plans, 
                "col_length": col_length,
                "key": settings.STRIPE_PUBLISHABLE_KEY,
                "is_active_member": is_active_member
                })
        else:
            return render(request, "no_auth.html", {})

    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            plans = get_paid_plans()
            col_length = math.floor(12.0 / len(plans))
            coupon_code = request.POST.get("coupon_code", '')
            if len(coupon_code) > 0:
                coupon = SubscriptionCouponCode.objects.filter(code=coupon_code).first()
                if coupon is not None and coupon.curr_redeems < coupon.max_redeems:
                    user = request.user
                    subscription = user.subscription
                    subscription.plan_type = 'ASKER'
                    subscription.initiated_on = datetime.now()
                    subscription.terminated_on = coupon.expiration_date
                    subscription.save()
                    coupon.curr_redeems = coupon.curr_redeems + 1
                    coupon.save()
                    # reactivate questions if needeed
                    self.reactivate_questions(user)
                    return render(request, self.template_name, {
                        "plans": plans, 
                        "col_length": col_length,
                        "key": settings.STRIPE_PUBLISHABLE_KEY,
                        "success": "You are successfully enrolled as a creator. Your plan type is " + str(subscription.plan_type),
                        "is_active_member": True
                        })
                else:
                    is_active_member = request.user.is_authenticated and request.user.subscription.plan_type != 'SHY' and request.user.subscription.terminated_on > datetime.now(timezone.utc)
                    return render(request, self.template_name, {
                        "plans": plans, 
                        "col_length": col_length,
                        "key": settings.STRIPE_PUBLISHABLE_KEY,
                        "message": "Coupon code expired or invalid",
                        "is_active_member": is_active_member
                        })

        return HttpResponseRedirect("/interview_questions/")

def make_payment(request):
    template_name = 'registration/enroll.html' 
    if request.method == 'POST':
        plans = get_paid_plans()
        col_length = math.floor(12.0 / len(plans))
        if not request.user.is_authenticated:
            return render(request, template_name, {
                        "plans": plans, 
                        "col_length": col_length,
                        "key": settings.STRIPE_PUBLISHABLE_KEY,
                        "message": "You are not logged in",
                        "is_active_member": False
                        })
        if ('amount' not in request.POST or 'description' not in request.POST or 'stripeToken' not in request.POST):
            is_active_member = request.user.is_authenticated and request.user.subscription.plan_type != 'SHY' and request.user.subscription.terminated_on > datetime.now(timezone.utc)
            return render(request, template_name, {
                        "plans": plans, 
                        "col_length": col_length,
                        "key": settings.STRIPE_PUBLISHABLE_KEY,
                        "message": "There was an error processing your payment",
                        "is_active_member": is_active_member
                        })

        stripe.api_key = settings.STRIPE_SECRET_KEY 
        amount = request.POST['amount']
        description = request.POST['description']
        stripe_token = request.POST['stripeToken']

        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            description=description,
            source=stripe_token
        )
        if charge:
            # edit the user and make them a member
            plan = get_plan_by_price(float(amount)/100)
            user = request.user
            subscription = user.subscription
            # see if user is currently on plan
            now = datetime.now(timezone.utc)
            is_on_plan = subscription.terminated_on and subscription.plan_type != 'SHY' and subscription.terminated_on > now
            # see if on plan and changing
            if is_on_plan and subscription.plan_type != plan:
                # reset termination to be 31 days from now and change plan type
                end_date = now + timedelta(days=31)
                subscription.plan_type = plan
                subscription.terminated_on = end_date
                subscription.save()
                user.save()
                # reactivate questions if needeed
                self.reactivate_questions(user)
                return render(request, template_name, {
                            "plans": plans, 
                            "col_length": col_length,
                            "key": settings.STRIPE_PUBLISHABLE_KEY,
                            "success": "You are successfully enrolled as a creator. Your plan type is " + str(plan),
                            "is_active_member": True
                            })
            else:
                # see if termination day - if so then start after terminated
                end = now
                if is_on_plan:
                        end = subscription.terminated_on
                        is_on_plan = True
                end_date = end + timedelta(days=31)

                if not is_on_plan:
                    subscription.initiated_on = now

                subscription.plan_type = plan
                subscription.terminated_on = end_date
                subscription.save()
                user.save()
                # reactivate questions if needeed
                self.reactivate_questions(user)
                return render(request, template_name, {
                            "plans": plans, 
                            "col_length": col_length,
                            "key": settings.STRIPE_PUBLISHABLE_KEY,
                            "success": "You are successfully enrolled as a creator. Your plan type is " + str(plan),
                            "is_active_member": True
                            })
        else:
            is_active_member = request.user.is_authenticated and request.user.subscription.plan_type != 'SHY' and request.user.subscription.terminated_on > datetime.now(timezone.utc)
            return render(request, template_name, {
                        "plans": plans, 
                        "col_length": col_length,
                        "key": settings.STRIPE_PUBLISHABLE_KEY,
                        "message": "There was an error processing your payment",
                        "is_active_member": is_active_member
                        })

class AccountView(View):
    template_name = 'info/account.html'   
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            terminated_time = ""
            if request.user.is_from_company:
                 is_active_member = request.user.is_authenticated and request.user.subscription.plan_type != 'SHY' and request.user.subscription.terminated_on > datetime.now(timezone.utc)
                 if is_active_member:
                     terminated_time = request.user.subscription.terminated_on.strftime('%b %d, %Y, %I:%M%p') + " (UTC Timezone)"
            return render(request, self.template_name, {"user": request.user, "terminated_time": terminated_time})
        return HttpResponseRedirect("/")

    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            first_name = request.POST.get("first_name", '')
            last_name = request.POST.get("last_name", '')
            if len(first_name) > 0 and len(last_name) > 0:
                user = SiteUser.objects.filter(email=request.user.email).first()
                if user is not None:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
        return HttpResponseRedirect("/")
