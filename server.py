#!/usr/bin/env python3
"""Ultra-minimal config-echo server for TCP-Railway VLESS.

Routes:
  GET /            -> plain-text: which port xray runs on + how to build a link
  GET /config?host=HOST:PORT  -> the ready vless:// link (plain text)
  GET /api/status  -> JSON: {"xray":bool,"port":int,"uuid":str}

Serves on :8080 (Railway HTTP domain); xray runs separately on XRAY_PORT (5432).
"""
import asyncio
import json
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", os.environ.get("UI_PORT", "8080")))
XRAY_PORT = int(os.environ.get("XRAY_PORT", "5432"))
UUID = os.environ.get("UUID", "8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234")

# ensure UI port never collides with the xray port
if PORT == XRAY_PORT:
    PORT = 8080


def vless_link(hostport):
    hostport = hostport.strip()
    # strip a leading "vless://" scheme if present (string-prefix, not lstrip chars)
    if hostport.startswith("vless://"):
        hostport = hostport[len("vless://"):]
    hostport = hostport.lstrip("@")
    return (f"vless://{UUID}@{hostport}"
            f"?security=none&type=tcp&headerType=none&encryption=none"
            f"#tcp-railway")


async def probe_xray():
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection("127.0.0.1", XRAY_PORT), timeout=2.0)
        w.close()
        return True
    except Exception:
        return False


def _send(writer, body, ctype="text/plain; charset=utf-8", code=200):
    reason = {200: "OK", 400: "Bad Request"}[code]
    resp = (f"HTTP/1.1 {code} {reason}\r\nContent-Type: {ctype}\r\n"
            f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
            f"{body}").encode()
    writer.write(resp)


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
        query = target.split("?", 1)[1] if "?" in target else ""

        if path == "/api/status":
            body = json.dumps({"xray": await probe_xray(),
                               "port": XRAY_PORT, "uuid": UUID})
            _send(writer, body, "application/json")
            await writer.drain()
            writer.close()
            return

        if path == "/config":
            # parse ?host=HOST:PORT
            host = ""
            for kv in query.split("&"):
                if kv.startswith("host="):
                    host = kv.split("=", 1)[1].replace("+", " ").strip()
            if not host:
                body = ("error: pass ?host=HOST:PORT "
                        "(e.g. /config?host=sakura.proxy.rlwy.net:17505)")
                _send(writer, body, code=400)
            else:
                _send(writer, vless_link(host))
            await writer.drain()
            writer.close()
            return

        # / -> plain instructions
        body = (
            "TCP-Railway VLESS\n"
            "=================\n"
            "xray (VLESS over raw TCP) listens on:\n"
            f"  host: 0.0.0.0    port: {XRAY_PORT}    uuid: {UUID}\n\n"
            "On Railway, add a TCP Proxy whose INTERNAL port = "
            f"{XRAY_PORT},\nand note its PUBLIC port (e.g. sakura.proxy.rlwy.net:17505).\n\n"
            "Build the client link:\n"
            f"  GET /config?host=YOUR_HOST:PORT\n"
            "where YOUR_HOST:PORT is the TCP proxy public address.\n"
            "Example:\n"
            "  /config?host=sakura.proxy.rlwy.net:17505\n\n"
            "=> returns a ready vless:// link to import.\n"
        )
        _send(writer, body)
        await writer.drain()
        writer.close()
    except Exception:
        try:
            writer.close()
        except Exception:
            pass


async def main():
    srv = await asyncio.start_server(handle, HOST, PORT)
    print(f"[ui] http://{HOST}:{PORT}  xray_port={XRAY_PORT}")
    async with srv:
        await srv.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
