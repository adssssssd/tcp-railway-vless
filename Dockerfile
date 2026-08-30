FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates unzip && rm -rf /var/lib/apt/lists/*
RUN curl -L -o /tmp/xray.zip https://github.com/XTLS/Xray-core/releases/download/v26.3.27/Xray-linux-64.zip && \
    unzip /tmp/xray.zip -d /tmp/xray && cp /tmp/xray/xray /usr/local/bin/xray && chmod +x /usr/local/bin/xray && rm -rf /tmp/xray*
RUN mkdir -p /app/xray
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
EXPOSE 5432
CMD ["/app/entrypoint.sh"]
