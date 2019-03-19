"""
Base class for all websockets.
"""
from io import BytesIO, StringIO
from typing import List, Optional, Union

import anyio
from wsproto import ConnectionType, WSConnection
from wsproto.events import (
    AcceptConnection,
    BytesMessage,
    CloseConnection,
    Message,
    Request,
    TextMessage,
)


class Websocket:
    _scope = None

    def __init__(self):
        self._byte_buffer = BytesIO()
        self._string_buffer = StringIO()
        self._closed = False

    async def __ainit__(
        self, addr, path: str, headers: Optional[List] = None, **connect_kw
    ):
        self._sock = await anyio.connect_tcp(*addr, **connect_kw)

        self._connection = WSConnection(ConnectionType.CLIENT)
        if headers is None:
            headers = []
        data = self._connection.send(
            Request(host=addr[0], target=path, extra_headers=headers)
        )
        await self._sock.send_all(data)

        assert self._scope is None
        self._scope = True
        try:
            event = await self._next_event()
            if not isinstance(event, AcceptConnection):
                raise ConnectionError("Failed to establish a connection", event)
        finally:
            self._scope = None

    async def _next_event(self):
        """
        Gets the next event.
        """
        while True:
            for event in self._connection.events():
                if isinstance(event, Message):
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
                return CloseConnection(code=500, reason="Socket closed")
            self._connection.receive_data(data)

    async def close(self, code: int = 1006, reason: str = "Connection closed"):
        """
        Closes the websocket.
        """
        if self._closed:
            return

        self._closed = True

        if self._scope is not None:
            await self._scope.cancel()
            # cancel any outstanding listeners

        data = self._connection.send(CloseConnection(code=code, reason=reason))
        await self._sock.send_all(data)

        # No, we don't wait for the correct reply
        await self._sock.close()

    async def send(self, data: Union[bytes, str], final: bool = True):
        """
        Sends some data down the connection.
        """
        if isinstance(data, str):
            data = TextMessage(data=data)
        else:
            data = BytesMessage(data=data)
        data = self._connection.send(event=data)
        await self._sock.send_all(data)

    def _buffer(self, event: Message):
        """
        Buffers an event, if applicable.
        """
        if isinstance(event, BytesMessage):
            self._byte_buffer.write(event.data)
        elif isinstance(event, TextMessage):
            self._string_buffer.write(event.data)

    def _gather_buffers(self, event: Message):
        """
        Gathers all the data from a buffer.
        """
        if isinstance(event, BytesMessage):
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
            return TextMessage(data=data, frame_finished=True, message_finished=True)
        elif isinstance(data, bytes):
            return BytesMessage(data=data, frame_finished=True, message_finished=True)

    async def __aiter__(self):
        async with anyio.open_cancel_scope() as scope:
            if self._scope is not None:
                raise RuntimeError("Only one task may iterate on this web socket")
            self._scope = scope
            try:
                while True:
                    msg = await self._next_event()
                    if isinstance(msg, CloseConnection):
                        return
                    yield msg
            finally:
                self._scope = None
