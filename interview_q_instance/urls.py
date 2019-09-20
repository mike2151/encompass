from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('', views.AllQuestionsToAnswerView.as_view()),
    path('/<int:pk>/', views.QuestionAnswerView.as_view()),
    path('/submit_test_case/<int:pk>/', views.UserTestCaseView.as_view(), name="submit_test_case"),
]