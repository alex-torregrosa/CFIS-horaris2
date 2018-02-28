"""Routing module"""
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from .consumers import GenerationConsumer


application = ProtocolTypeRouter({
    # WebSocket  handler
    "websocket":
        URLRouter([
            url("^$", GenerationConsumer),
        ]),
})
