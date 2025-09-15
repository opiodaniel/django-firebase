from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/client-screen/$', consumers.ClientScreenConsumer.as_asgi()),
    re_path(r'ws/client-screen/(?P<order_id>\w+)/$', consumers.ClientScreenConsumer.as_asgi()),
]