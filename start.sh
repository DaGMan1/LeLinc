#!/bin/sh
set -e

export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 &

./cloak/entrypoint.sh &

uvicorn agents.cookie_grant:app --host 0.0.0.0 --port 8000 &

uvicorn agents.orchestrator:app --host 0.0.0.0 --port 8001 &

nginx -g "daemon off;"
