"""
Client connection utilities.
"""

from asyncwebsockets.websocket import Websocket

try:
    from contextlib import acontextmanager
except ImportError:
    from async_generator import asynccontextmanager as acontextmanager


@acontextmanager
async def open_websocket_server(sock, filter=None):  # pylint: disable=W0622
    """
    A context manager which serves this websocket.

    :param filter: an async callback which accepts the connection request
    and returns a bool, or an explicit Accept/Reject message.
    """
    ws = await create_websocket_server(sock, filter=filter)
    try:
        yield ws
    finally:
        await ws.close()


async def create_websocket_server(sock, filter=None):  # pylint: disable=W0622
    """
    A more low-level form of open_websocket_server.
    You are responsible for closing this websocket.
    """
    ws = Websocket()
    await ws.start_server(sock, filter=filter)
    return ws
