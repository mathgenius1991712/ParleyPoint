from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/private_chat/(?P<username>\w+)/$', consumers.PrivateChatConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<username>\w+)/$', consumers.NotificationConsumer.as_asgi()),
]