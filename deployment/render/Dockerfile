# Render free tier (512 MB): the site and API in one container, serving the example runs.
# The model needs about 2 GB, so there is no worker and uploads are switched off.
# Built from the repo root: docker build -f deployment/render/Dockerfile .
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
# Empty means the browser calls /api on the same host, which nginx passes to the API.
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*
COPY --from=web /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install . huggingface_hub
ARG SEED_REPO=abhishek1402/avia-demo
RUN python -c "from huggingface_hub import snapshot_download as d; \
d('$SEED_REPO', repo_type='dataset', local_dir='/app/seed', allow_patterns=['avia.db', 'files/*'])"
COPY --from=web /web/.next/standalone ./web
COPY --from=web /web/.next/static ./web/.next/static
COPY --from=web /web/public ./web/public
COPY artifacts/benchmarks.json ./artifacts/benchmarks.json
COPY deployment/render/nginx.conf deployment/render/start.sh ./
RUN chmod +x start.sh
ENV DATABASE_URL=sqlite:////data/avia.db \
    STORAGE_DIR=/data/files \
    BENCHMARKS_PATH=/app/artifacts/benchmarks.json \
    UPLOADS_OPEN=0
EXPOSE 10000
CMD ["./start.sh"]
