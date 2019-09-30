from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('<int:pk>/', views.SubmissionView.as_view()),
    path('submissions/<int:pk>/', views.CreatorSubmissionResult.as_view()),
]