#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/neurox-ai
mkdir -p backend/data

if ! pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  nohup uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 > /tmp/neurox-api.log 2>&1 &
fi

if ! pgrep -f "next dev" >/dev/null 2>&1; then
  nohup npm run dev -- --hostname 0.0.0.0 > /tmp/neurox-web.log 2>&1 &
fi
