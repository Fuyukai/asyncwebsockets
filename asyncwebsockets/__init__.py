"""
asyncwebsockets - an asynchronous library for handling websockets.
"""
import importlib
import multio


def _find_asyncws_class():
    """
    Finds the appropriate class for the current library.
    """
    path = "asyncwebsockets._specific." + multio.asynclib.lib_name
    mod = importlib.import_module(path)
    ws_classname = "{}Websocket".format(multio.asynclib.lib_name.title())
    return getattr(mod, ws_classname)
