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
    ws = None
    try:
        ws = await create_websocket(url)
        yield ws
    finally:
        if ws is not None:
            await ws.close()


async def create_websocket(url: str):
    """
    A more low-level form of websocket. You are responsible for closing this websocket.
    """
    url = yarl.URL(url)
    # automatically use ssl if it's websocket secure
    ssl = url.scheme == "wss"
    addr = (url.host, int(url.port))
    ws = Websocket()
    await ws.__ainit__(addr=addr, ssl=ssl, path=url.path)

    event = await ws.next_event()
    if not isinstance(event, ConnectionEstablished):
        raise ConnectionError("Failed to establish a connection")

    return ws


try:
    import curio.meta
    curio.meta.safe_generator(open_websocket.__wrapped__)
except ImportError:
    pass
