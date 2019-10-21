from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live_interview/(?P<instance_id>\w+)/(?P<live_interview_id>\w+)/$', consumers.InterviewConsumer),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})