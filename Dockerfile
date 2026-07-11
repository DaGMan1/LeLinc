FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    chromium \
    xvfb \
    fonts-liberation \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/
COPY cloak/ ./cloak/
COPY nginx/ ./nginx/
COPY start.sh .

RUN chmod +x start.sh cloak/entrypoint.sh \
    && rm -f /etc/nginx/sites-enabled/default \
    && cp nginx/default.conf /etc/nginx/conf.d/default.conf \
    && mkdir -p /cookies /profile

# 80 = dashboard/onboarding, 8000 = Cookie Grant API, 8001 = Orchestrator + QC API.
# Cloak's CDP port is intentionally not exposed here - internal-only, no VNC.
EXPOSE 80 8000 8001

ENTRYPOINT ["./start.sh"]
