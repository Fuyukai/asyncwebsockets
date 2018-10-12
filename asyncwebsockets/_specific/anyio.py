"""
Websocket implementation for trio
"""
import anyio
from typing import Union
from wsproto import events
from wsproto.connection import WSConnection, ConnectionType

from asyncwebsockets.websocket import Websocket


class AnyioWebsocket(Websocket):
    async def __ainit__(self, addr, path: str, *, ssl: bool = True):
        if ssl:
            self._sock = await anyio.connect_tcp(*addr, tls=True)
        else:
            self._sock = await anyio.connect_tcp(*addr, tls=False)

        self._cancel_scopes = set()
        self._connection = WSConnection(ConnectionType.CLIENT, host=addr[0], resource=path)

        # start the handshake
        data = self._connection.bytes_to_send()
        await self._sock.send_all(data)

    async def next_event(self):
        """
        Gets the next event.
        """
        async with anyio.open_cancel_scope() as scope:
            self._cancel_scopes.add(scope)
            try:
                while True:
                    for event in self._connection.events():
                        if isinstance(event, events.DataReceived):
                            # check if we need to buffer
                            if event.message_finished:
                                return self._wrap_data(self._gather_buffers(event))
                            else:
                                self._buffer(event)
                                break  # exit for loop
                        else:
                            return event

                    data = await self._sock.receive_some(4096)
                    self._connection.receive_bytes(data)
            finally:
                self._cancel_scopes.remove(scope)

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
        self._sock.close()
        # cancel any outstanding listeners
        for scope in self._cancel_scopes:
            scope.cancel()

        self._cancel_scopes.clear()

    async def send(self, data: Union[bytes, str], final: bool = True):
        """
        Sends some data down the connection.
        """
        self._connection.send_data(payload=data, final=True)
        data = self._connection.bytes_to_send()
        await self._sock.send_all(data)
