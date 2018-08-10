"""
Base class for all websockets.
"""
from async_generator import async_generator, yield_
from io import BytesIO, StringIO

import abc
from typing import Any, Union
from wsproto.events import DataReceived, BytesReceived, TextReceived, ConnectionRequested, \
    ConnectionEstablished, ConnectionClosed, ConnectionFailed, PingReceived, PongReceived


class Websocket(abc.ABC):
    """
    A base websocket.
    """

    def __init__(self):
        self._byte_buffer = BytesIO()
        self._string_buffer = StringIO()
        self._closed = False

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

    @abc.abstractmethod
    async def __ainit__(self, *args, **kwargs):
        """
        Async initializes this websocket. This is automatically called by :meth:`.open_websocket`.
        """

    @abc.abstractmethod
    async def next_event(self) -> \
        Union[DataReceived, ConnectionRequested, ConnectionEstablished, ConnectionClosed,
              ConnectionFailed, PingReceived, PongReceived]:
        """
        Gets the next event from this websocket.
        """

    @abc.abstractmethod
    async def close(self, code: int = 1006, reason: str = "Connection closed"):
        """
        Closes this websocket.

        :param code: The close code to use.
        :param reason: The close reason to use.
        """
        if self._closed:
            return

    @abc.abstractmethod
    async def send(self, data: Union[bytes, str]):
        """
        Sends data down this websocket.
        """

    @async_generator
    async def __aiter__(self):
        while True:
            await yield_(await self.next_event())
