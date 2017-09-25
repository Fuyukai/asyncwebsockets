"""
Websocket client functions.
"""
from urllib.parse import urlparse

import multio
from wsproto.connection import WSConnection, ConnectionType

from asyncwebsockets.common import Websocket


async def connect_websocket(url: str = None, *,
                            host: str = None, port: int = None,
                            endpoint: str = None, ssl: bool = False) -> Websocket:
    """
    Connects a websocket to a server.

    You can provide the URL using either:
    :param url: The URL to connect to.

    Or the individual parts:
    :param host: The host to connect to.
    :param port: The port to connect to.
    :param endpoint: The endpoint to connect to.
    :param ssl: If SSL should be used to connect.

    :return: A :class:`.Websocket` connected to the server.
    """
    if url is not None:
        # decompose URL into individual parts
        split = urlparse(url)
        ssl = split.scheme == "wss"

        # try and detect host/port automatically
        try:
            host, port = split.netloc.split(":")
            port = int(port)
        except ValueError:
            host = split.netloc
            port = 443 if split.scheme == "wss" else 80

        endpoint = split.path + "?" + split.query

    sock = await multio.asynclib.open_connection(host=host, port=port, ssl=ssl)
    sock = multio.SocketWrapper(sock)
    state = WSConnection(conn_type=ConnectionType.CLIENT, host=host, resource=endpoint)

    websocket = Websocket(state, sock)
    await websocket.open()
    return websocket
