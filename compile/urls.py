from compile.views import CompileCodeView
from django.urls import path
urlpatterns = [
    path('code/', CompileCodeView.as_view())
]