#!/bin/bash
set -euo pipefail

# ---- xray: VLESS over raw TCP on the port the Railway TCP proxy maps to ----
UUID="${UUID:-8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234}"
XRAY_PORT="${XRAY_PORT:-5432}"

cat > /app/xray/config.json <<EOF
{
  "log": {"loglevel": "warning"},
  "inbounds": [{
    "listen": "0.0.0.0",
    "port": ${XRAY_PORT},
    "protocol": "vless",
    "settings": {"clients": [{"id": "${UUID}", "flow": ""}], "decryption": "none"},
    "streamSettings": {"network": "tcp", "security": "none", "tcpSettings": {"header": {"type": "none"}}}
  }],
  "outbounds": [{"protocol": "freedom", "settings": {}}]
}
EOF

echo "[entrypoint] VLESS TCP on :${XRAY_PORT} uuid=${UUID}"

# ---- start xray in background ----
/usr/local/bin/xray run -c /app/xray/config.json > /app/xray.log 2>&1 &
XRAY_PID=$!
sleep 2
if ! kill -0 "$XRAY_PID" 2>/dev/null; then
  echo "[entrypoint] FATAL: xray failed" >&2
  cat /app/xray.log >&2
  exit 1
fi
echo "[entrypoint] xray up (pid $XRAY_PID)"

# ---- UI server in foreground (Railway maps :8080) ----
PORT="${PORT:-8080}" XRAY_PORT="${XRAY_PORT}" exec python3 /app/server.py
