#!/usr/bin/env python3
"""
VectorCraft Trace Lab - Localhost Test Environment
Runs on standard Python 3 http.server with zero external pip dependencies.
"""

import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
import vectorcraft_trace

PORT = int(os.environ.get("PORT", 8765))

class TraceLabHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/trace":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body)
                data_uri = payload.get("image")
                params = payload.get("params", {})

                if not data_uri:
                    self._send_json({"error": "No image data provided"}, status=400)
                    return

                res = vectorcraft_trace.trace_base64(
                    data_uri,
                    mode=params.get("mode", "color"),
                    colors=params.get("colors", 16),
                    threshold=params.get("threshold", 128),
                    ignore_white=params.get("ignore_white", True),
                    palette=params.get("palette", "automatic"),
                    paths=params.get("paths", 50),
                    corners=params.get("corners", 50),
                    noise=params.get("noise", 25),
                    strokes=params.get("strokes", False),
                    stroke_width=params.get("stroke_width", 10.0),
                    shapes=params.get("shapes", False),
                    auto_grouping=params.get("auto_grouping", False),
                    method=params.get("method", "abutting"),
                )
                self._send_json(res)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _send_json(self, data, status=200):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

def run():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, TraceLabHandler)
    print(f"VectorCraft Trace Lab running at: http://127.0.0.1:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Trace Lab.")
        httpd.server_close()

if __name__ == "__main__":
    run()
