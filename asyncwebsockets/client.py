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
async def open_websocket(url: str, headers: Optional[list] = None):
    """
    Opens a websocket.
    """
    ws = None
    try:
        ws = await create_websocket(url, headers=headers)
        yield ws
    finally:
        if ws is not None:
            await ws.close()


async def create_websocket(
    url: str, ssl: Optional[SSLContext] = None, headers: Optional[list] = None
):
    """
    A more low-level form of websocket. You are responsible for closing this websocket.
    """
    url = yarl.URL(url)
    args = {}
    if headers:
        args["headers"] = headers

    # automatically use ssl if it's websocket secure
    if ssl is None:
        ssl = url.scheme == "wss"
    if ssl:
        if ssl is True:
            ssl = SSLContext()
        args["ssl_context"] = ssl
        args["autostart_tls"] = True
        args["tls_standard_compatible"] = False

    addr = (url.host, int(url.port))
    ws = Websocket()
    await ws.__ainit__(addr=addr, path=url.path_qs, **args)
    return ws


try:
    import curio.meta

    curio.meta.safe_generator(open_websocket.__wrapped__)
except ImportError:
    pass
