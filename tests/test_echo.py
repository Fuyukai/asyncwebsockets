from wsproto.events import BytesMessage, TextMessage, Message

import trio
import pytest
from asyncwebsockets import Websocket
from asyncwebsockets.client import open_websocket
from asyncwebsockets.client import create_websocket_client
from asyncwebsockets.server import open_websocket_server


@pytest.mark.trio
async def test_echo():
    async with open_websocket("ws://echo.websocket.org") as sock:
        await sock.send(b"test")
        rcvd = 0
        async for message in sock:
            print("Event received", message)
            if isinstance(message, BytesMessage):
                assert message.data == b"test"
                rcvd += 1
                await sock.close(code=1000, reason="Thank you!")

        assert rcvd == 1


@pytest.mark.trio
async def test_local_echo():
    async with trio.open_nursery() as n:
        async def serve_one(s):
            async with open_websocket_server(s) as w:
                async for m in w:
                    if isinstance(m,Message):
                        await w.send(m.data)
                    else:
                        break

        async def serve(task_status=trio.TASK_STATUS_IGNORED):
            listeners = await trio.open_tcp_listeners(0)
            task_status.started(listeners)
            while True:
                s = await listeners[0].accept()
                n.start_soon(serve_one, s)

        listeners = await n.start(serve)
        conn = await trio.testing.open_stream_to_socket_listener(listeners[0])

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


@pytest.mark.trio
async def test_secure_echo():
    async with open_websocket("wss://echo.websocket.org") as sock:
        await sock.send("test")
        rcvd = 0
        async for message in sock:
            print("Event received", message)

            if isinstance(message, TextMessage):
                assert message.data == "test"
                rcvd += 1
                await sock.close(code=1000, reason="Thank you!")
        assert rcvd == 1


