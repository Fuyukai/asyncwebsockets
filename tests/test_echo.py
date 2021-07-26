from wsproto.events import BytesMessage, TextMessage, Message

import anyio
import pytest
from asyncwebsockets.client import open_websocket
from asyncwebsockets.client import create_websocket_client
from asyncwebsockets.server import open_websocket_server


@pytest.mark.anyio
async def test_echo():
    async with open_websocket("ws://echo.websocket.org") as sock:  # pylint: disable=E1701
        await sock.send(b"test")
        rcvd = 0
        async for message in sock:
            print("Event received", message)
            if isinstance(message, BytesMessage):
                assert message.data == b"test"
                rcvd += 1
                await sock.close(code=1000, reason="Thank you!")

        assert rcvd == 1


@pytest.mark.anyio
async def test_local_echo():
    async with anyio.create_task_group() as n:

        async def serve_one(s):
            async with open_websocket_server(s) as w:  # pylint: disable=E1701
                async for m in w:
                    if isinstance(m, Message):
                        await w.send(m.data)
                    else:
                        break

        async def serve(*, task_status):
            listeners = await anyio.create_tcp_listener(local_port=0)
            task_status.started(listeners)
            await listeners.serve(serve_one)

        listeners = await n.start(serve)
        addr = listeners.extra(anyio.abc.SocketAttribute.local_address)
        conn = await anyio.connect_tcp(*addr)

        sock = await create_websocket_client(conn, "localhost", "/", subprotocols=["echo"])
        await sock.send(b"test")
        rcvd = 0
        async for message in sock:
            print("Event received", message)
            if isinstance(message, BytesMessage):
                assert message.data == b"test"
                rcvd += 1
                await sock.close(code=1000, reason="Thank you!")

        assert rcvd == 1
        n.cancel_scope.cancel()
        await sock.close()


@pytest.mark.anyio
async def test_secure_echo():
    async with open_websocket("wss://echo.websocket.org") as sock:  # pylint: disable=E1701
        await sock.send("test")
        rcvd = 0
        async for message in sock:
            print("Event received", message)

            if isinstance(message, TextMessage):
                assert message.data == "test"
                rcvd += 1
                await sock.close(code=1000, reason="Thank you!")
        assert rcvd == 1
