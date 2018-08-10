"""
Client connection utilities.
"""
import yarl
from wsproto.events import ConnectionEstablished

from asyncwebsockets._specific import Websocket

try:
    from contextlib import acontextmanager
except ImportError:
    from async_generator import asynccontextmanager as acontextmanager


@acontextmanager
async def open_websocket(url: str):
    """
    Opens a websocket.
    """
    url = yarl.URL(url)
    # automatically use ssl if it's websocket secure
    ssl = url.scheme == "wss"
    addr = (url.host, int(url.port))
    ws = Websocket()
    await ws.__ainit__(addr=addr, ssl=ssl, path=url.path)

    try:
        event = await ws.next_event()
        if not isinstance(event, ConnectionEstablished):
            raise ConnectionError("Failed to establish a connection")
        yield ws
    finally:
        await ws.close()
