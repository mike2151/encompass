from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view()),
]