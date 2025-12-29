import threading
import time
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.probe import is_http_reachable

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/system_stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b"{}")
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, port

class Var:
    def __init__(self, v):
        self.v = str(v)
    def get(self):
        return self.v

class App:
    def __init__(self, port):
        self.custom_port = Var(port)

def main():
    srv, port = start_server()
    app = App(port)
    ok = is_http_reachable(app)
    print("reachable:", ok)
    assert ok
    srv.shutdown()
    time.sleep(0.1)
    ok2 = is_http_reachable(app)
    print("after_shutdown:", ok2)
    assert not ok2

if __name__ == "__main__":
    main()