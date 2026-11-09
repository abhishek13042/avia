#!/bin/sh
# Space disk is reset on restart, so the example runs are copied back from the image each time.
set -e
mkdir -p "$HOME/data"
[ -f "$HOME/data/avia.db" ] || cp -r /app/seed/. "$HOME/data/"

python -m avia.worker.main &
uvicorn avia.api.main:app --host 127.0.0.1 --port 8000 &
PORT=3000 HOSTNAME=127.0.0.1 node /app/web/server.js &
nginx -c /app/nginx.conf -g "daemon off;" &

# If any part stops, stop the container so the Space restarts it.
wait -n 2>/dev/null || wait
exit 1
