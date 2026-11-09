#!/bin/sh
# The free tier has no persistent disk, so the example runs are copied in on every start.
set -e
mkdir -p /data
[ -f /data/avia.db ] || cp -r /app/seed/. /data/

uvicorn avia.api.main:app --host 127.0.0.1 --port 8000 &
PORT=3000 HOSTNAME=127.0.0.1 node /app/web/server.js &
nginx -c /app/nginx.conf -g "daemon off;" &

# If any part stops, stop the container so Render restarts it.
wait -n 2>/dev/null || wait
exit 1
