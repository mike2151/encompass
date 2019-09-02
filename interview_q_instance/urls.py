from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('', views.AllQuestionsToAnswerView.as_view()),
    path('/<int:pk>/', views.QuestionAnswerView.as_view())
]