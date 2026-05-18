ARG OPENCLAW_BASE_IMAGE
FROM ${OPENCLAW_BASE_IMAGE}

USER root
WORKDIR /app

COPY openclaw/config /app/openclaw/config
COPY openclaw/scripts /app/openclaw/scripts

RUN chmod +x /app/openclaw/scripts/*.sh \
 && mkdir -p /home/node/.openclaw /tmp/openclaw \
 && chown -R node:node /app/openclaw /home/node/.openclaw /tmp/openclaw

USER node

ENTRYPOINT ["/app/openclaw/scripts/entrypoint.sh"]
