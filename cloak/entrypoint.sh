#!/bin/sh
set -e

CLIENT_ID="${CLIENT_ID:-default}"
CDP_PORT="${CLOAK_CDP_PORT:-9222}"

mkdir -p "/cookies/${CLIENT_ID}" /profile

# The patched Chromium binary lives under a version-specific directory that
# changes on `cloakbrowser update` - resolve it at runtime instead of
# hardcoding a version.
CLOAK_BIN="$(find /root/.cloakbrowser -maxdepth 2 -name chrome -type f | head -1)"
if [ -z "$CLOAK_BIN" ]; then
  echo "Cloak Browser binary not found under /root/.cloakbrowser - was 'python -m cloakbrowser install' run at build time?" >&2
  exit 1
fi

# Stealth comes from source-level patches baked into this specific binary,
# not from launch flags - so this is otherwise a normal Chromium invocation.
# CDP is bound to localhost only - internal use by cdp_handler.py, never
# exposed as a container port. No VNC, no direct external access.
"$CLOAK_BIN" \
  --headless=new \
  --disable-gpu \
  --no-sandbox \
  --remote-debugging-port="${CDP_PORT}" \
  --remote-debugging-address=127.0.0.1 \
  --remote-allow-origins=http://127.0.0.1:${CDP_PORT} \
  --user-data-dir=/profile \
  --window-size=1920,1080 &

CLOAK_PID=$!

python3 cloak/cdp_handler.py --wait-and-load-cookies --client-id "$CLIENT_ID" --cdp-port "$CDP_PORT"

wait "$CLOAK_PID"
