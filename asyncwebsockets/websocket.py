"""
Base class for all websockets.
"""
# pylint: disable=R0913

from io import BytesIO, StringIO
from typing import List, Optional, Union

import anyio
from wsproto import ConnectionType, WSConnection
from wsproto.events import (
    AcceptConnection,
    RejectConnection,
    BytesMessage,
    CloseConnection,
    Message,
    Request,
    TextMessage,
)


class Websocket:
    _scope = None
    _sock = None
    _connection = None

    def __init__(self):
        self._byte_buffer = BytesIO()
        self._string_buffer = StringIO()
        self._closed = False

    async def __ainit__(
        self, addr, path: str, headers: Optional[List] = None, subprotocols=None, **connect_kw
    ):
        sock = await anyio.connect_tcp(*addr, **connect_kw)
        await self.start_client(sock, addr, path=path, headers=headers, subprotocols=subprotocols)

    async def start_client(
        self,
        sock: anyio.abc.SocketStream,
        addr,
        path: str,
        headers: Optional[List] = None,
        subprotocols: Optional[List[str]] = None,
    ):
        """Start a client WS connection on this socket.

        Returns: the AcceptConnection message.
        """
        self._sock = sock
        self._connection = WSConnection(ConnectionType.CLIENT)
        if headers is None:
            headers = []
        if subprotocols is None:
            subprotocols = []
        data = self._connection.send(
            Request(host=addr[0], target=path, extra_headers=headers, subprotocols=subprotocols)
        )
        try:
            await self._sock.send_all(data)
        except AttributeError:
            await self._sock.send(data)

        assert self._scope is None
        self._scope = True
        try:
            event = await self._next_event()
            if not isinstance(event, AcceptConnection):
                raise ConnectionError("Failed to establish a connection", event)
            return event
        finally:
            self._scope = None

    async def start_server(
        self, sock: anyio.abc.SocketStream, filter=None
    ):  # pylint: disable=W0622
        """Start a server WS connection on this socket.

        Filter: an async callable that gets passed the initial Request.
        It may return an AcceptConnection message, a bool, or a string (the
        subprotocol to use).
        Returns: the Request message.
        """
        assert self._scope is None
        self._scope = True
        self._sock = sock
        self._connection = WSConnection(ConnectionType.SERVER)

        try:
            event = await self._next_event()
            if not isinstance(event, Request):
                raise ConnectionError("Failed to establish a connection", event)
            msg = None
            if filter is not None:
                msg = await filter(event)
                if not msg:
                    msg = RejectConnection()
                elif msg is True:
                    msg = None
                elif isinstance(msg, str):
                    msg = AcceptConnection(subprotocol=msg)
            if not msg:
                msg = AcceptConnection(subprotocol=event.subprotocols[0])
            data = self._connection.send(msg)
            try:
                await self._sock.send_all(data)
            except AttributeError:
                await self._sock.send(data)
            if not isinstance(msg, AcceptConnection):
                raise ConnectionError("Not accepted", msg)
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
                    self._buffer(event)
                    break  # exit for loop
                else:
                    return event

            try:
                data = await self._sock.receive_some(4096)
            except AttributeError:
                data = await self._sock.receive(4096)
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
        try:
            await self._sock.send_all(data)
        except AttributeError:
            await self._sock.send(data)

        # No, we don't wait for the correct reply
        try:
            await self._sock.close()
        except AttributeError:
            await self._sock.aclose()

    async def send(self, data: Union[bytes, str], final: bool = True):
        """
        Sends some data down the connection.
        """
        MsgType = TextMessage if isinstance(data, str) else BytesMessage
        data = MsgType(data=data, message_finished=final)
        data = self._connection.send(event=data)
        try:
            await self._sock.send_all(data)
        except AttributeError:
            await self._sock.send(data)

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

    @staticmethod
    def _wrap_data(data: Union[str, bytes]):
        """
        Wraps data into the right event.
        """
        MsgType = TextMessage if isinstance(data, str) else BytesMessage
        return MsgType(data=data, frame_finished=True, message_finished=True)

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
