import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

from src.scans import ports
from src import port_scan


def test_port_scans_detect_open_port():
    server = HTTPServer(("0.0.0.0", 80), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    try:
        time.sleep(0.2)  # allow server to start
        result_module = ports.scan("127.0.0.1")
        assert 80 in result_module["details"].get("open_ports", [])

        result_util = port_scan.scan_ports("127.0.0.1")
        assert 80 in result_util
    finally:
        server.shutdown()
        thread.join()
