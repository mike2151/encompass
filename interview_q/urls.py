from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('create/', views.CreateInterviewView.as_view()),
    path('', views.HomeInterviewView.as_view()),
    path('question/<int:pk>/edit/', views.EditQuestionView.as_view()),
    path('question/<int:pk>/send/', views.CreateQuestionInstanceView.as_view())
]