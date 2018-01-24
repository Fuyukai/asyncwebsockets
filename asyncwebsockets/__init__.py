"""
Websocket library for curio + trio.
"""
from asyncwebsockets.client import connect_websocket
from asyncwebsockets.ws import ClientWebsocket, WebsocketClosed, \
    WebsocketMessage, WebsocketTextMessage, WebsocketBytesMessage, WebsocketConnectionEstablished, \
    WebsocketConnectionFailed

__all__ = ["connect_websocket", "ClientWebsocket",
           "WebsocketClosed", "WebsocketBytesMessage", "WebsocketTextMessage", "WebsocketMessage",
           "WebsocketConnectionEstablished", "WebsocketConnectionFailed"]
