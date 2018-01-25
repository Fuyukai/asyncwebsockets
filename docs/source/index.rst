.. asyncwebsockets documentation master file, created by
   sphinx-quickstart on Wed Jan 24 23:59:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to asyncwebsockets's documentation!
===========================================

asyncwebsockets is a Python 3.6+ library for interacting with websockets over the internet from
asynchronous code. asyncwebsockets is designed around `multio`_, allowing it to work with
multiple async backends without any modifications.

Installation
============

To install the latest stable version::

    $ pip install asyncwebsockets

To install the latest development version::

    $ pip install git+https://github.com/SunDwarf/asyncwebsockets.git#egg=asyncwebsockets


Basic Usage
===========

To open a new websocket connection to a server, use :func:`.connect_websocket`:

.. autofunction:: asyncwebsockets.client.connect_websocket
    :async:

This will return a new :class:`.ClientWebsocket`, which is the main object used for communication
with the server.

You can get new events from the websocket by async iteration over the websocket object, like so:

.. code-block:: python3

    async for evt in websocket:
        print(type(evt))  # handle event appropriately

You can send data to the websocket in response with :meth:`.ClientWebsocket.send_message`:

.. code-block:: python3

    async for evt in websocket:
        if isinstance(evt, WebsocketBytesMessage):
            await websocket.send_message(b"Thanks for the message!")

.. automethod:: asyncwebsockets.ws.ClientWebsocket.send_message
    :async:

Finally, the websocket can be closed with the usage of :meth:`.ClientWebsocket.close`:

.. code-block:: python3

    await websocket.close(1000, reason="Goodbye!")

.. automethod:: asyncwebsockets.ws.ClientWebsocket.close

Event Listing
=============

A full listing of events that can be yielded from the websockets can be found here.

.. py:currentmodule:: asyncwebsockets.ws

.. autoclass:: WebsocketMessage
.. autoclass:: WebsocketTextMessage
.. autoclass:: WebsocketBytesMessage
.. autoclass:: WebsocketClosed
.. autoclass:: WebsocketConnectionEstablished
.. autoclass:: WebsocketConnectionFailed

Changelog
=========

0.2.0
-----

 - Redesign API significantly.

0.1.0
-----

 - Initial release.


.. _multio: https://github.com/theelous3/multio