"""
Common code for both client and server.
"""
import collections
import enum
from io import BytesIO, StringIO
from typing import Union

import multio
from wsproto import events
from wsproto.connection import WSConnection


class MessageType(enum.Enum):
    """
    Represents the type of a message.
    """
    TEXT = 0
    BYTES = 1


class WebsocketMessage:
    """
    Represents a message.
    """
    def __init__(self, data: Union[str, bytes]):
        self.data = data


class WebsocketTextMessage(WebsocketMessage):
    """
    Represents a plaintext based message.
    """
    TYPE = MessageType.TEXT


class WebsocketBytesMessage(WebsocketMessage):
    """
    Represents a binary bytes based message.
    """
    TYPE = MessageType.BYTES


class WebsocketUnusable(RuntimeError):
    """
    Exception that's raised when a websocket cannot be read or written to.

    This is raised when the websocket is closed.
    """


class WebsocketClosed(Exception):
    """
    Exception that represents a websocket that's closed.
    """
    def __init__(self, code: int = 1000, reason: str = "No reason"):
        """
        :param code: The close code provided.
        :param reason: The close reason provided.
        """
        #: The close code.
        self.code = code

        #: The close reason.
        self.reason = reason


class Websocket(object):
    """
    A websocket is a socket based around a frame-based protocol, originally designed for
    web browsers. This class implements common logic between client and server.

    This class should not be created directly - it should be returned from
    :meth:`.connect_websocket` or :meth:`.serve_websocket`.
    """
    def __init__(self, state: WSConnection, sock: multio.SocketWrapper):
        """
        :param state: The :class:`wsproto.connection.WSConnection` that has been setup.
        :param sock: The socket object that has been opened.
        """
        self.state = state
        self.sock = sock

        self._ready = False
        self._messages = collections.deque()
        self._byte_buffer = BytesIO()
        self._string_buffer = StringIO()

    @property
    def closed(self) -> bool:
        """
        :return: If this websocket is closed.
        """
        return self.state.closed

    async def open(self):
        """
        Opens the websocket.
        """
        # self.state.initiate_connection()
        to_send = self.state.bytes_to_send()
        await self.sock.sendall(to_send)

        # read open event
        msg = await self.next_message()
        if not isinstance(msg, events.ConnectionEstablished):
            raise WebsocketUnusable("Got unknown open event {}".format(msg))

        self._ready = True

    async def next_message(self) -> WebsocketMessage:
        """
        Gets the next message from this websocket.

        :return: A :class:`.WebsocketMessage` object that represents the message received.
        """
        if self.closed:
            raise WebsocketUnusable("Websocket is closed")

        # if we can, pop off an event
        try:
            return self._messages.popleft()
        except IndexError:
            pass

        # temporary deque for messages received since
        messages = collections.deque()

        while True:
            # read 8192 bytes off the sock
            try:
                data = await self.sock.recv(8192)
            except OSError as e:
                raise WebsocketUnusuable("Read error") from e
            self.state.receive_bytes(data)

            need_data = False
            for event in self.state.events():
                if isinstance(event, events.ConnectionClosed):
                    raise WebsocketClosed(code=event.code, reason=event.reason)

                if isinstance(event, events.ConnectionEstablished):
                    return event

                if isinstance(event, events.ConnectionFailed):
                    raise WebsocketClosed(code=event.code, reason=event.reason)

                # do some buffer handling
                # TODO: Make this cleaner.
                if isinstance(event, events.BytesReceived):
                    self._byte_buffer.write(event.data)

                    if event.message_finished:
                        val = self._byte_buffer.getvalue()
                        self._byte_buffer = BytesIO()

                        message = WebsocketBytesMessage(val)
                        messages.append(message)
                    else:
                        # go around for another loop
                        need_data = True

                elif isinstance(event, events.TextReceived):
                    self._string_buffer.write(event.data)

                    if event.message_finished:
                        val = self._string_buffer.getvalue()
                        self._string_buffer = StringIO()

                        message = WebsocketTextMessage(val)
                        messages.append(message)
                    else:
                        # go around for another loop
                        need_data = True

            # break if we have a message, and have at least one message
            if messages and not need_data:
                break

        next_message = messages.popleft()
        if messages:
            self._messages.extend(messages)

        return next_message

    async def send_message(self, data: Union[str, bytes]):
        """
        Sends a message on the websocket.

        :param data: The data to send. Either str or bytes.
        """
        if self.closed:
            raise WebsocketUnusable("Websocket is closed")

        self.state.send_data(data, final=True)
        await self.sock.sendall(self.state.bytes_to_send())

    async def close(self, *, code: int = 1000, reason: str = "No reason"):
        """
        Closes the websocket.

        :param code: The close code to use.
        :param reason: The close reason to use.
        """
        self.state.close(code=code, reason=reason)
        to_send = self.state.bytes_to_send()
        await self.sock.sendall(to_send)
        await self.sock.close()
        self.state.receive_bytes(None)

