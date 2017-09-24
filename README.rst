asyncws
=======

asyncws is a `curio`_ + `trio`_ compatible library for connecting and serving websockets.


Installation
------------

To install the latest stable version::

    $ pip install asyncws

To install the latest development version::

    $ pip install git+https://github.com/SunDwarf/asyncws.git#egg=asyncws


Basic Usage
-----------

.. code-block:: python

    import multio
    from asyncws import open_websocket, Websocket

    async def main():
        sock: Websocket = await connect_websocket("wss://echo.websocket.org")
        await sock.send_message("Hello, world!")
        ev = await sock.next_message()
        print(ev.data)  # "Hello, world!"
        await sock.close(code=1000, reason="Goodbye")

    multio.init("curio")
    multio.run(main)

.. _curio: https://curio.readthedocs.io/en/latest/
.. _trio: https://trio.readthedocs.io/en/latest/
