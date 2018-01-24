asyncwebsockets
=======

asyncwebsockets is a `curio`_ + `trio`_ compatible library for connecting and serving websockets.


Installation
------------

To install the latest stable version::

    $ pip install asyncwebsockets

To install the latest development version::

    $ pip install git+https://github.com/SunDwarf/asyncwebsockets.git#egg=asyncwebsockets


Basic Usage
-----------

.. code-block:: python3

    import multio

    from asyncwebsockets.client import connect_websocket
    from asyncwebsockets.ws import WebsocketConnectionEstablished, WebsocketBytesMessage

    async def test():
        sock = await connect_websocket("wss://echo.websocket.org", reconnecting=False)
        async for message in sock:
            print("Event received", message)
            if isinstance(message, WebsocketConnectionEstablished):
                await sock.send_message(b"test")

            elif isinstance(message, WebsocketBytesMessage):
                print("Got response:", message.data)
                await sock.close(code=1000, reason="Thank you!")


    multio.init("curio")
    multio.run(main)

.. _curio: https://curio.readthedocs.io/en/latest/
.. _trio: https://trio.readthedocs.io/en/latest/
