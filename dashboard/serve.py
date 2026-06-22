#!/usr/bin/env python3
"""Mini server pro prototyp dashboardu: serveruje složku dashboard/ na portu 8731.
Spuštění:  python3 dashboard/serve.py   → http://localhost:8731/
"""
import http.server
import os
import socketserver

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8731


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Dashboard běží na http://localhost:{PORT}/")
        httpd.serve_forever()
