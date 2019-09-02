from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('create/', views.CreateInterviewView.as_view()),
    path('', views.HomeInterviewView.as_view()),
    path('question/<int:pk>/', views.IndividualQuestionView.as_view()),
    path('<int:pk>/create_instance', views.CreateQuestionInstanceView.as_view())
]