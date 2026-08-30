# ⚡ TCP-Railway VLESS

Xray **VLESS over raw TCP** on Railway — bypasses filtering through a Railway
**TCP proxy** (`*.proxy.rlwy.net:<port>`), with **zero WebSocket and zero TLS**.
Because the Railway domain isn't filtered, this is the *fastest, most direct*
route: client → Railway TCP proxy → xray.

This is the **exact same config** running on the author's live box (VLESS-TCP
on internal port `5432`, fixed UUID).

---

## Deploy

1. Push this repo to Railway (Dockerfile installs Xray 26.3.27 + tiny server).
2. **Networking**:
   * **TCP Proxy** → public port `17505` (or any) → **internal port `5432`**
     (where xray listens). Note the public host:port, e.g.
     `sakura.proxy.rlwy.net:17505`.
   * **HTTP** → your `*.up.railway.app` domain → port `8080` (tiny config UI).
3. Done.

> Override UUID via env `UUID`, xray port via env `XRAY_PORT` (default `5432`).

---

## Tiny config UI (no HTML)

Open your Railway HTTP domain:

* `GET /` — tells you which port xray runs on and how to build the link.
* `GET /config?host=HOST:PORT` — returns a **ready vless:// link** (plain text),
  e.g. `GET /config?host=sakura.proxy.rlwy.net:17505`
* `GET /api/status` — `{"xray":true,"port":5432,"uuid":"..."}`

---

## Client config (manual)

```
vless://8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234@sakura.proxy.rlwy.net:17505?security=none&type=tcp&headerType=none&encryption=none#tcp-railway
```

---

## Layout

* `Dockerfile` — debian + Xray 26.3.27 + python3
* `entrypoint.sh` — writes xray config, starts xray (bg) + tiny UI (fg)
* `server.py` — plain-text `/`, `/config`, `/api/status`
