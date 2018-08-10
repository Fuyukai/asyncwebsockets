import multio


def Websocket(*args, **kwargs):
    if multio.asynclib.lib_name == "curio":
        from asyncwebsockets._specific.curio import CurioWebsocket
        return CurioWebsocket(*args, **kwargs)
    elif multio.asynclib.lib_name == "trio":
        from asyncwebsockets._specific.trio import TrioWebsocket
        return TrioWebsocket(*args, **kwargs)
