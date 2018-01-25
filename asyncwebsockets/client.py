"""
Websocket client functions.
"""
from urllib.parse import urlparse

from asyncwebsockets.ws import ClientWebsocket


async def connect_websocket(url: str = None, *,
                            host: str = None, port: int = None,
                            endpoint: str = None, ssl: bool = False,
                            reconnecting: bool = True) -> ClientWebsocket:
    """
    Connects a websocket to a server.

    You can provide the URL using either:

    :param url: The URL to connect to.

    Or the individual parts:

    :param host: The host to connect to.
    :param port: The port to connect to.
    :param endpoint: The endpoint to connect to.
    :param ssl: If SSL should be used to connect.

    This also accepts some additional options:

    :param reconnecting: If this websocket should automatically reconnect.

    :return: A :class:`.ClientWebsocket` connected to the server.
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

    websocket = ClientWebsocket((host, port, ssl, endpoint),
                                reconnecting=reconnecting)
    await websocket.open_connection()
    return websocket
