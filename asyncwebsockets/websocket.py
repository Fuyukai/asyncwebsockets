"""
Base class for all websockets.
"""
from io import BytesIO, StringIO
import anyio

from typing import Union
from wsproto.events import DataReceived, BytesReceived, TextReceived, ConnectionRequested, \
    ConnectionEstablished, ConnectionClosed, ConnectionFailed, PingReceived, PongReceived

from wsproto.connection import WSConnection, ConnectionType

class Websocket:
    _scope = None

    def __init__(self):
        self._byte_buffer = BytesIO()
        self._string_buffer = StringIO()
        self._closed = False

    async def __ainit__(self, addr, path: str, **connect_kw):
        self._sock = await anyio.connect_tcp(*addr, **connect_kw)

        self._connection = WSConnection(ConnectionType.CLIENT, host=addr[0], resource=path)

        # start the handshake
        data = self._connection.bytes_to_send()
        await self._sock.send_all(data)

        assert self._scope is None
        self._scope = True
        try:
            event = await self._next_event()
            if not isinstance(event, ConnectionEstablished):
                raise ConnectionError("Failed to establish a connection", event)
        finally:
            self._scope = None


    async def _next_event(self):
        """
        Gets the next event.
        """
        while True:
            for event in self._connection.events():
                print("EVT:",event)
                if isinstance(event, DataReceived):
                    # check if we need to buffer
                    if event.message_finished:
                        return self._wrap_data(self._gather_buffers(event))
                    else:
                        self._buffer(event)
                        break  # exit for loop
                else:
                    return event

            data = await self._sock.receive_some(4096)
            if not data:
                return ConnectionFailed(500,"Socket closed")
            self._connection.receive_bytes(data)

    async def close(self, code: int = 1006, reason: str = "Connection closed"):
        """
        Closes the websocket.
        """
        if self._closed:
            return

        self._closed = True

        self._connection.close(code=code, reason=reason)
        data = self._connection.bytes_to_send()
        await self._sock.send_all(data)
        await self._sock.close()
        if self._scope is not None:
            await self._scope.cancel()
            # cancel any outstanding listeners

    async def send(self, data: Union[bytes, str], final: bool = True):
        """
        Sends some data down the connection.
        """
        self._connection.send_data(payload=data, final=True)
        data = self._connection.bytes_to_send()
        await self._sock.send_all(data)

    def _buffer(self, event: DataReceived):
        """
        Buffers an event, if applicable.
        """
        if isinstance(event, BytesReceived):
            self._byte_buffer.write(event.data)
        elif isinstance(event, TextReceived):
            self._string_buffer.write(event.data)

    def _gather_buffers(self, event: DataReceived):
        """
        Gathers all the data from a buffer.
        """
        if isinstance(event, BytesReceived):
            buf = self._byte_buffer
        else:
            buf = self._string_buffer

        # yay for code shortening
        buf.write(event.data)
        buf.seek(0)
        data = buf.read()
        buf.seek(0)
        buf.truncate()
        return data

    def _wrap_data(self, data: Union[str, bytes]):
        """
        Wraps data into the right event.
        """
        if isinstance(data, str):
            return TextReceived(data, True, True)
        elif isinstance(data, bytes):
            return BytesReceived(data, True, True)

    async def __aiter__(self):
        async with anyio.open_cancel_scope() as scope:
            if self._scope is not None:
                raise RuntimeError("Only one task may iterate on this web socket")
            self._scope = scope
            try:
                while True:
                    msg = await self._next_event()
                    if isinstance(msg, (ConnectionFailed, ConnectionClosed)):
                        return
                    yield msg
            finally:
                self._scope = None

