.. asyncwebsockets documentation master file, created by
   sphinx-quickstart on Wed Jan 24 23:59:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to asyncwebsockets's documentation!
===========================================

asyncwebsockets is a Python 3.6+ library for interacting with websockets over the internet from
asynchronous code. asyncwebsockets is designed around `anyio`_, allowing it to work with
multiple async backends without any modifications.

asyncwebsockets supports client and server mode.

Installation
============

To install the latest stable version::

    $ pip install asyncwebsockets

To install the latest development version::

    $ pip install git+https://github.com/Fuyukai/asyncwebsockets.git#egg=asyncwebsockets


Basic Usage
===========

Client connection
-----------------

To open a new websocket connection to a server, use :func:`.open_websocket`:

.. autofunction:: asyncwebsockets.client.open_websocket
    :async:

This async context manager returns a new :class:`.Websocket`, which is the
main object used for communication with the server.

You can use :func:`.create_websocket` if using a context manager is
inconvenient, but then you're responsible for closing it.

.. autofunction:: asyncwebsockets.client.create_websocket
    :async:

The functions :func:`.create_websocket_client` and :func:`.open_websocket.client`
accept an existing socket instead of a URL.

.. autofunction:: asyncwebsockets.client.open_websocket_client
    :async:

.. autofunction:: asyncwebsockets.client.create_websocket_client
    :async:

Server connection
-----------------

Likewise, :func:`.create_websocket_server` and
:func:`.open_websocket.server` accept an existing socket to act as a
Websocket server.

.. autofunction:: asyncwebsockets.server.open_websocket_server
    :async:

.. autofunction:: asyncwebsockets.server.create_websocket_server
    :async:

asyncwebsockets does not provide server equivalents of
:func:`.open_websocket` or :func:`.create_websocket`; use whatever method
is most convenient for your code.

Data transfer
-------------

After being established, a Websocket connection is bidirectional and does
no longer distinguish between client and server roles.

You get new events from the websocket by async iteration over the websocket object:

.. code-block:: python3

    async for evt in websocket:
        print(type(evt))  # handle event appropriately

See the ``wsproto.events`` documentation for message types.

You can send data (strings or bytes) to the websocket in response with :meth:`.ClientWebsocket.send_message`:

.. code-block:: python3

    from wsproto.events import TextMessage

    async for evt in websocket:
       if isinstance(evt, TextMessage):
          await websocket.send("Thanks for saying '%s'!" % (evt.data,))

.. automethod:: asyncwebsockets.websocket.Websocket.send
    :async:

In short, you receive ``TextMessage`` or ``ByteMessage`` messages,
depending on the payload. You can also filter for ``Message`` instances,
and discern between strings and bytes by checking the type of the ``.data``
attribute.

Finally, the websocket can be closed with the usage of :meth:`.ClientWebsocket.close`:

.. code-block:: python3

    await websocket.close(1000, reason="Goodbye!")

.. automethod:: asyncwebsockets.websocket.Websocket.close

Event Listing
=============

Events are the standard wsproto events.


Changelog
=========

0.5.0
-----

 - Add server mode
 - Add ability to take over an existing socket

0.4.0
-----

 - Adapt to current wsproto design

0.3.0
-----

 - Redesign API, again, hopefully for the last time.

0.2.0
-----

 - Redesign API significantly.

0.1.0
-----

 - Initial release.


.. _anyio: https://github.com/theelous3/anyio
