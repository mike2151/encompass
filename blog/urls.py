from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.BlogHomePageView.as_view()),
    path('<int:pk>/', views.BlogPostView.as_view()),
]