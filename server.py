#!/usr/bin/env python3
"""Serve TCP-Railway VLESS UI + status/probe APIs, alongside xray.

Routes:
  /             -> index.html (the English UI)
  /api/status   -> JSON: {"router":true,"xray":bool,"port":int}
  /api/probe    -> POST {"host","port"} -> {"ok":bool}  (raw TCP connect test)
"""
import asyncio
import json
import os
import socket

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
XRAY_PORT = int(os.environ.get("XRAY_PORT", "5432"))

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")


async def probe_host(host, port, timeout=3.0):
    """Raw TCP connect test (returns True if the port accepts connections)."""
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout)
        w.close()
        return True
    except Exception:
        return False


async def handle(reader, writer):
    try:
        req = await reader.read(65536)
        if not req:
            writer.close()
            return
        line = req.split(b"\r\n", 1)[0].decode("latin-1", "replace")
        parts = line.split(" ")
        if len(parts) < 2:
            writer.close()
            return
        method, target = parts[0], parts[1]
        path = target.split("?")[0]

        if path == "/api/status":
            body = json.dumps({
                "router": True,
                "xray": await probe_host("127.0.0.1", XRAY_PORT),
                "port": XRAY_PORT,
            }).encode()
            resp = (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    b"Access-Control-Allow-Origin: *\r\nContent-Length: "
                    + str(len(body)).encode() + b"\r\n\r\n" + body)
            writer.write(resp)
            await writer.drain()
            writer.close()
            return

        if path == "/api/probe" and method == "POST":
            body_bytes = req.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in req else b""
            try:
                payload = json.loads(body_bytes.decode("utf-8", "replace") or "{}")
            except Exception:
                payload = {}
            host = (payload.get("host") or "").strip()
            try:
                port = int(payload.get("port", 443))
            except Exception:
                port = 443
            ok = bool(host) and await probe_host(host, port)
            body = json.dumps({"ok": ok, "host": host, "port": port}).encode()
            resp = (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    b"Access-Control-Allow-Origin: *\r\nContent-Length: "
                    + str(len(body)).encode() + b"\r\n\r\n" + body)
            writer.write(resp)
            await writer.drain()
            writer.close()
            return

        # default: serve index.html
        try:
            with open(INDEX, "rb") as f:
                body = f.read()
        except FileNotFoundError:
            body = b"index.html not found"
        resp = (b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n"
                b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
        writer.write(resp)
        await writer.drain()
        writer.close()
    except Exception:
        try:
            writer.close()
        except Exception:
            pass


async def main():
    srv = await asyncio.start_server(handle, HOST, PORT)
    print(f"[ui-srv] http://{HOST}:{PORT}  (xray_port={XRAY_PORT})")
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
