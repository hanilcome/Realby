from django.urls import re_path

from livechat import consumers

websocket_urlpatterns = [
    re_path(r'ws/livechat/(?P<room_name>\w+)/$', consumers.LiveChatConsumer.as_asgi()),
]