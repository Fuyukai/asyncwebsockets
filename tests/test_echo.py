from wsproto.events import BytesMessage, TextMessage

import pytest
from asyncwebsockets.client import open_websocket


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
