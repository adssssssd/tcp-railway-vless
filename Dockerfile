FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates unzip python3 && rm -rf /var/lib/apt/lists/*
RUN curl -L -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/download/v26.3.27/Xray-linux-64.zip && \
    unzip /tmp/xray.zip -d /tmp/xray && cp /tmp/xray/xray /usr/local/bin/xray && chmod +x /usr/local/bin/xray && rm -rf /tmp/xray*
RUN mkdir -p /app/xray
COPY entrypoint.sh /app/entrypoint.sh
COPY server.py /app/server.py
RUN chmod +x /app/entrypoint.sh
# xray VLESS-TCP (internal; Railway TCP proxy maps here -> 5432)
EXPOSE 5432
# tiny config-echo UI (Railway HTTP domain -> 8080)
EXPOSE 8080
CMD ["/app/entrypoint.sh"]
