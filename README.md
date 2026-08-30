# ⚡ TCP Railway VLESS

Xray **VLESS over raw TCP** on Railway — bypasses filtering through a Railway
**TCP proxy** (`*.proxy.rlwy.net:<port>`), with **zero WebSocket and zero TLS**
layer. Since the Railway domain isn't filtered, this is the *fastest, most
direct* route: client → Railway TCP proxy → xray.

No Cloudflare Worker, no WS, no TLS handshake overhead.

---

## Deploy

1. Push this repo to Railway (or use any Railway service with a Dockerfile).
2. Add a **TCP Proxy** in Railway → service → **Networking**:
   * Public port: `<anything>` (e.g. `17505`) → **Internal port: `5432`**
3. Done.

> Override UUID / port via env `UUID` / `PORT`.

---

## Client config

```
vless://8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234@sakura.proxy.rlwy.net:17505?security=none&type=tcp&headerType=none&encryption=none#tcp-railway
```

Import into v2rayN / v2rayNG / Hiddify / Nekoray — that's it.

---

## Layout

* `Dockerfile` — debian + Xray 26.3.27
* `entrypoint.sh` — renders xray config from `UUID`/`PORT`, runs xray in foreground
