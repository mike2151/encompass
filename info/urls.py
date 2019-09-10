from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view()),
    path('about/', views.AboutPageView.as_view()),
]


