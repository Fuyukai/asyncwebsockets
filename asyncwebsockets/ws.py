"""
Common code for both client and server.
"""
from io import BytesIO, StringIO
from typing import Tuple, Union

import multio
from wsproto import events
from wsproto.connection import ConnectionType, WSConnection


class WebsocketMessage:
    """
    Represents a message.
    """


class WebsocketTextMessage(WebsocketMessage):
    """
    Represents a plaintext based message.
    """
    def __init__(self, data: str):
        #: The :class:`str` data for this text message.
        self.data = data


class WebsocketBytesMessage(WebsocketMessage):
    """
    Represents a binary bytes based message.
    """
    def __init__(self, data: bytes):
        #: The :class:`bytes` data for this text message.
        self.data = data


class WebsocketClosed(WebsocketMessage):
    """
    Represents a websocket close event.
    """

    def __init__(self, evt: events.ConnectionClosed):
        self.evt = evt

        #: The close code.
        self.code = evt.code  # type: int

        #: The close reason.
        self.reason = evt.reason  # type: str


class WebsocketConnectionEstablished(WebsocketMessage):
    """
    Represents a websocket connection established event.
    """

    def __init__(self, evt: events.ConnectionEstablished):
        #: The internal event.
        self.evt = evt


class WebsocketConnectionFailed(WebsocketMessage):
    """
    Represents a websocket connection failed message.
    """

    def __init__(self, evt: events.ConnectionFailed):
        #: The internal event.
        self.evt = evt


class ClientWebsocket(object):
    """
    Represents a ClientWebsocket.
    """

    def __init__(self, address: Tuple[str, str, bool, str], *, reconnecting: bool = True):
        """
        :param type_: The :class:`wsproto.connection.ConnectionType` for this websocket.
        :param address: A 4-tuple of (host, port, ssl, endpoint).
        :param endpoint: The endpoint to open the connection to.
        :param reconnecting: If this websocket reconnects automatically. Only useful on the client.
        """

        # these are all used to construct the state object
        self._address = address

        self.state = None  # type: WSConnection
        self._ready = False
        self._reconnecting = reconnecting
        self.sock = None  # type: multio.SocketWrapper

    @property
    def closed(self) -> bool:
        """
        :return: If this websocket is closed.
        """
        return self.state.closed

    async def open_connection(self):
        """
        Opens a connection, and performs the initial handshake.
        """
        _sock = await multio.asynclib.open_connection(self._address[0], self._address[1],
                                                      ssl=self._address[2])
        self.sock = multio.SocketWrapper(_sock)
        self.state = WSConnection(ConnectionType.CLIENT, host=self._address[0],
                                  resource=self._address[3])
        res = self.state.bytes_to_send()
        await self.sock.sendall(res)

    async def __aiter__(self):
        # initiate the websocket
        await self.open_connection()
        # setup buffers
        buf_bytes = BytesIO()
        buf_text = StringIO()

        while True:
            data = await self.sock.recv(4096)
            self.state.receive_bytes(data)

            # do ping/pongs if needed
            to_send = self.state.bytes_to_send()
            if to_send:
                await self.sock.sendall(to_send)

            for event in self.state.events():
                if isinstance(event, events.ConnectionEstablished):
                    self._ready = True
                    yield WebsocketConnectionEstablished(event)

                elif isinstance(event, events.ConnectionClosed):
                    self._ready = False
                    yield WebsocketClosed(event)

                    if self._reconnecting:
                        await self.open_connection()
                    else:
                        return

                elif isinstance(event, events.DataReceived):
                    buf = buf_bytes if isinstance(event, events.BytesReceived) else buf_text
                    buf.write(event.data)

                    # yield events as appropriate
                    if event.message_finished:
                        buf.seek(0)
                        read = buf.read()
                        # empty buffer
                        buf.truncate(0)
                        buf.seek(0)

                        typ = WebsocketBytesMessage if isinstance(event, events.BytesReceived) \
                            else WebsocketTextMessage
                        yield typ(read)

                elif isinstance(event, events.ConnectionFailed):
                    self._ready = False

                    yield WebsocketConnectionFailed(event)

                    if self._reconnecting:
                        await self.open_connection()
                    else:
                        return

    async def send_message(self, data: Union[str, bytes]):
        """
        Sends a message on the websocket.

        :param data: The data to send. Either str or bytes.
        """
        self.state.send_data(data, final=True)
        return await self.sock.sendall(self.state.bytes_to_send())

    async def close(self, *, code: int = 1000, reason: str = "No reason",
                    allow_reconnects: bool = False):
        """
        Closes the websocket.

        :param code: The close code to use.
        :param reason: The close reason to use.

        If the websocket is marked as reconnecting:

        :param allow_reconnects: If the websocket can reconnect after this close.
        """
        # do NOT reconnect if we close explicitly and don't allow reconnects
        if not allow_reconnects:
            self._reconnecting = False

        self.state.close(code=code, reason=reason)
        to_send = self.state.bytes_to_send()
        await self.sock.sendall(to_send)
        await self.sock.close()
        self.state.receive_bytes(None)
