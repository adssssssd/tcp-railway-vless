# ⚡ TCP Railway VLESS

Xray **VLESS over raw TCP** on Railway — bypasses filtering through a Railway
**TCP proxy** (`*.proxy.rlwy.net:<port>`), with **zero WebSocket and zero TLS**.
Since the Railway domain isn't filtered, this is the *fastest, most direct* route:
client → Railway TCP proxy → xray.

Comes with a **built-in English web UI** (config builder + live server status).

---

## Deploy

1. Push this repo to Railway (Dockerfile builds Xray + the web UI).
2. **Networking** on the service:
   * **Public HTTP** — your `*.up.railway.app` domain → port `8080` (the UI).
   * **TCP Proxy** → for the VLESS tunnel. Give it a public port (`17505`)
     and point its **internal port at `5432`** (where xray listens).
3. Done.

> Override UUID via env `UUID`, xray port via env `XRAY_PORT` (default `5432`).

---

## The UI

Open your Railway domain → it shows:
* **Live status** — whether xray & the server are up (green/red dot).
* **Which port to run it on** — the internal port the TCP proxy must target.
* **Config builder** — paste your `host:port` (e.g. `sakura.proxy.rlwy.net:17505`),
  press **Build config**, get a ready VLESS link, one click copy.

---

## Client config (manual)

```
vless://8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234@sakura.proxy.rlwy.net:17505?security=none&type=tcp&headerType=none&encryption=none#tcp-railway
```

---

## Layout

* `Dockerfile` — debian + Xray 26.3.27 + python server
* `entrypoint.sh` — renders xray config from `UUID`/`XRAY_PORT`, starts xray + UI
* `server.py` — serves the UI, `/api/status`, `/api/probe` (TCP reachability test)
* `index.html` — the English UI
