"""
Websocket implementation for curio.
"""
import curio
from typing import Union
from wsproto import events
from wsproto.connection import WSConnection, ConnectionType

from asyncwebsockets.websocket import Websocket


class CurioWebsocket(Websocket):
    async def __ainit__(self, addr, path: str, *, ssl: bool = True):
        self._sock = await curio.open_connection(*addr, ssl=ssl)
        self._connection = WSConnection(ConnectionType.CLIENT, host=addr[0], resource=path)

        # start the handshake
        data = self._connection.bytes_to_send()
        await self._sock.sendall(data)

    async def next_event(self):
        """
        Gets the next event.
        """
        while True:
            data = await self._sock.recv(4096)
            self._connection.receive_bytes(data)

            for event in self._connection.events():
                if isinstance(event, events.DataReceived):
                    # check if we need to buffer
                    if event.message_finished:
                        return self._wrap_data(self._gather_buffers(event))  # exit while loop
                    else:
                        self._buffer(event)
                        break  # exit for loop
                else:
                    return event

    async def close(self, code: int = 1006, reason: str = "Connection closed"):
        """
        Closes the websocket.
        """
        if self._closed:
            return

        self._closed = True

        self._connection.close(code=code, reason=reason)
        data = self._connection.bytes_to_send()
        await self._sock.sendall(data)
        await self._sock.close()

    async def send(self, data: Union[bytes, str], final: bool = True):
        """
        Sends some data down the connection.
        """
        self._connection.send_data(payload=data, final=True)
        data = self._connection.bytes_to_send()
        await self._sock.sendall(data)