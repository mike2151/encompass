from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('create/', views.CreateInterviewView.as_view()),
    path('', views.HomeInterviewView.as_view()),
    path('success/<success_message>/', views.HomeInterviewView.as_view(), name="success_all_interview_questions"),
    path('question/<int:pk>/edit/', views.EditQuestionView.as_view()),
    path('question/<int:pk>/submissions/', views.SubmissionsQuestionView.as_view()),
    path('question/<int:pk>/observe_answerers/', views.ObserveAnswerersView.as_view()),
    path('question/<int:pk>/delete/', views.DeleteQuestionView.as_view()),
    path('question/<int:pk>/send/', views.CreateQuestionInstanceView.as_view()),
    path('question/<int:pk>/try/', views.CreateOpenQuestionInstanceView.as_view()),
    path('question/<int:pk>/validate/', views.ValidateQuestionView.as_view()),
    path('open/', views.OpenQuestionView.as_view()),
]