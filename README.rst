asyncwebsockets
=======

asyncwebsockets is an `anyio`_-compatible websocket client library.
Thus it works with `curio`_, `trio`_, or ``asyncio``.


Installation
------------

To install the latest stable version::

    $ pip install asyncwebsockets

To install the latest development version::

    $ pip install git+https://github.com/Fuyukai/asyncwebsockets.git#egg=asyncwebsockets


Basic Usage
-----------

.. code-block:: python3

    import anyio
    import asyncwebsockets

    async def test():
        async with asyncwebsockets.open_websocket("wss://echo.websocket.org") as ws:
            await ws.send("test")
            evt = await ws.next_event()
            print(type(evt), getattr(evt, 'data', None))


    anyio.run(test)

.. _curio: https://curio.readthedocs.io/en/latest/
.. _trio: https://trio.readthedocs.io/en/latest/
.. _anyio: https://anyio.readthedocs.io/en/latest/
