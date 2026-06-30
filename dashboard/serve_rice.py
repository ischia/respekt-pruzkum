#!/usr/bin/env python3
"""Samostatný localhost pro RICE audit – stránka dashboard/RICE_vstupy.html.

Serveruje z kořene repa (kvůli fontům v prezentace/fonts/), na portu 8792.
Nezávislé na decku i na dashboardu. Spuštění:
    python3 dashboard/serve_rice.py   → http://localhost:8792/
"""
import http.server
import os
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8792
PAGE = "/dashboard/RICE_vstupy.html"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", PAGE)
            self.end_headers()
            return
        return super().do_GET()


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"RICE audit běží na http://localhost:{PORT}/")
        httpd.serve_forever()
