from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('/<int:pk>/', views.QuestionObserveView.as_view()),
]