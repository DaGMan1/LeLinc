#!/bin/sh
set -e

CLIENT_ID="${CLIENT_ID:-default}"
CDP_PORT="${CLOAK_CDP_PORT:-9222}"

mkdir -p "/cookies/${CLIENT_ID}" /profile

# CDP is bound to localhost only - internal use by cdp_handler.py, never exposed
# as a container port. No VNC, no direct external access to the browser.
chromium \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --remote-debugging-port="${CDP_PORT}" \
  --remote-debugging-address=127.0.0.1 \
  --remote-allow-origins=http://127.0.0.1:${CDP_PORT} \
  --user-data-dir=/profile \
  --window-size=1920,1080 &

CHROME_PID=$!

python3 cloak/cdp_handler.py --wait-and-load-cookies --client-id "$CLIENT_ID" --cdp-port "$CDP_PORT"

wait "$CHROME_PID"
