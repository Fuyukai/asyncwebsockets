"""
Client connection utilities.
"""
from ssl import SSLContext
from typing import Optional

import yarl

from asyncwebsockets.websocket import Websocket

try:
    from contextlib import acontextmanager
except ImportError:
    from async_generator import asynccontextmanager as acontextmanager


@acontextmanager
async def open_websocket_server(sock, filter=None):
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


async def create_websocket_server(sock, filter=None):
    """
    A more low-level form of open_websocket_server.
    You are responsible for closing this websocket.
    """
    ws = Websocket()
    await ws.start_server(sock, filter=filter)
    return ws


try:
    import curio.meta

    curio.meta.safe_generator(open_websocket_server.__wrapped__)
except ImportError:
    pass
