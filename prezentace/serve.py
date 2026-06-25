#!/usr/bin/env python3
"""Servíruje reveal.js prezentaci na portu 8790.
Spuštění:  python3 prezentace/serve.py   → http://localhost:8790/
(reveal načítá slides.md přes fetch, takže nestačí otevřít soubor přes file://)
"""
import http.server
import os
import socketserver

DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8790


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Prezentace běží na http://localhost:{PORT}/")
        httpd.serve_forever()
