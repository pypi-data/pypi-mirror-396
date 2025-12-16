import sys

# for path in sys.path.copy():
#     if path != "/usr/lib/python3.8" and \
#        path != "/usr/lib/python3.8/lib-dynload" and \
#        (not ("vspyx" in path)) and \
#        (not ("Prebuilt/Filesystem" in path)):
#         sys.path.remove(path)

import asyncio
import threading
import vspyx
from tornado import ioloop, process, web, websocket
from pyls_jsonrpc import dispatchers, endpoint
from pyls.python_ls import PythonLanguageServer
from io import StringIO

try:
    import ujson as json
except ImportError:  # pylint: disable=broad-except
    import json

TAG = "PythonLanguageServer"

class LanguageServerWebSocketHandler(websocket.WebSocketHandler):
    """Setup tornado websocket handler to host language server."""

    def open(self, *args, **kwargs):
        vspyx.Core.Log(TAG).d("Creating new language server")
        self.pyls = PythonLanguageServer(StringIO, StringIO)
        self._endpoint = endpoint.Endpoint(self.pyls, lambda msg: self.write_message(json.dumps(msg)))

    def on_message(self, msg):
        """Forward client->server messages to the endpoint."""
        ''' msg = {"jsonrpc":"2.0","method":"$/cancelRequest","params":{"id":51}} '''
        #print("msg =", msg)
        ''' type(msg) = <class 'str'> '''
        #print("type(msg) =", type(msg))
        if $VERBOSE or (not "$/cancelRequest" in msg):
            self._endpoint.consume(json.loads(msg))
        #vspyx.Core.Log(TAG).d(f"client->server: ${message}")

    def check_origin(self, origin):
        return True

class TornadoServer:

    def start(self):
        vspyx.Core.Log(TAG).d("Starting the Python Language Server daemon")
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        app = web.Application([
            (r"/python", LanguageServerWebSocketHandler),
        ])
        app.listen($PORT, address="127.0.0.1")
        self.io_loop = ioloop.IOLoop.current()
        self.io_loop.start()

    def stop(self):
        if self.io_loop is not None:
            self.io_loop.add_callback(self.io_loop.stop)
            self.thread.join()

TORNADO = None
if __name__ == '__main__':
    TORNADO = TornadoServer()
    TORNADO.start()

def stop_tornado():
    if TORNADO is not None:
        TORNADO.stop()
