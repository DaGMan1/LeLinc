FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    fonts-unifont \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    curl \
    ca-certificates \
    zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install-deps chromium \
    && python -m cloakbrowser install

COPY agents/ ./agents/
COPY cloak/ ./cloak/
COPY nginx/ ./nginx/
COPY extension/ ./extension/
COPY start.sh .

RUN chmod +x start.sh cloak/entrypoint.sh \
    && rm -f /etc/nginx/sites-enabled/default \
    && cp nginx/default.conf /etc/nginx/conf.d/default.conf \
    && mkdir -p /cookies /profile nginx/downloads \
    && cd extension && zip -r ../nginx/downloads/lelinc-extension.zip . -x "README.md" && cd ..

# 80 = dashboard/onboarding, 8000 = Cookie Grant API, 8001 = Orchestrator + QC API.
# Cloak's CDP port is intentionally not exposed here - internal-only, no VNC.
EXPOSE 80 8000 8001

ENTRYPOINT ["./start.sh"]
