#!/usr/bin/env bash
set -euo pipefail
# Xray VLESS over TCP on the port a Railway TCP proxy maps to.
# External: viaduct.proxy.rlwy.net:<PORT>  ->  internal :PORT (xray)
UUID="${UUID:-8f2c1e6a-4b7d-4a9e-b3f1-c5d8e7a91234}"
PORT="${PORT:-5432}"
cat > /app/xray/config.json <<EOF
{
  "log": {"loglevel": "warning"},
  "inbounds": [{
    "listen": "0.0.0.0",
    "port": ${PORT},
    "protocol": "vless",
    "settings": {"clients": [{"id": "${UUID}", "flow": ""}], "decryption": "none"},
    "streamSettings": {"network": "tcp", "security": "none", "tcpSettings": {"header": {"type": "none"}}}
  }],
  "outbounds": [{"protocol": "freedom", "settings": {}}]
}
EOF
echo "[entrypoint] VLESS TCP on :${PORT} uuid=${UUID}"
exec /usr/local/bin/xray run -c /app/xray/config.json
