from django.urls import include, path, re_path
from django.conf import settings
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('enroll/', views.EnrollView.as_view(), name="enroll"),
    path('enroll_in_membership/', views.enroll_in_membership, name="enroll_in_membership"),
    path('cancel_auto_renewal/', views.cancel_auto_renewal, name="cancel_auto_renewal"),
    path('activate_auto_renewal/', views.activate_auto_renewal, name="activate_auto_renewal"),
    path('account/', views.AccountView.as_view()),
    re_path(r'^logout/$', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]