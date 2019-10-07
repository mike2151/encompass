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
from datetime import datetime

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
            error_messages.append("passwords must be longer than 8 characters")

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
                return HttpResponseRedirect("/")
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
    template_name = 'registration/enroll.html'   
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, self.template_name, {})
        else:
            return render(request, "no_auth.html", {})

    def post(self, request,  *args, **kwargs):
        if request.user.is_authenticated:
            coupon_code = request.POST.get("coupon_code", '')
            if len(coupon_code) > 0:
                coupon = SubscriptionCouponCode.objects.filter(code=coupon_code).first()
                if coupon is not None and coupon.curr_redeems < coupon.max_redeems:
                    user = request.user
                    subscription = user.subscription
                    subscription.plan_type = 'MONTHLY_CREATOR'
                    subscription.initiated_on = datetime.now()
                    subscription.terminated_on = coupon.expiration_date
                    subscription.save()
                    coupon.curr_redeems = coupon.curr_redeems + 1
                    coupon.save()
                else:
                    return render(request, self.template_name, {"message": "Coupon code expired or invalid"})

        return HttpResponseRedirect("/interview_questions/")
