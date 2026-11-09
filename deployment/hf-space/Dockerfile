# One container for a Hugging Face Space: nginx on 7860 in front of the site, API and worker.
# Built from the folder that scripts/stage_hf_space.py assembles, not from the repo root.
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
ARG PUBLIC_URL=https://abhishek1402-avia.hf.space
ENV NEXT_PUBLIC_API_URL=$PUBLIC_URL
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 nginx \
    && rm -rf /var/lib/apt/lists/*
COPY --from=web /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install .
COPY --from=web /web/.next/standalone ./web
COPY --from=web /web/.next/static ./web/.next/static
COPY --from=web /web/public ./web/public
COPY model ./model
COPY artifacts ./artifacts
COPY seed ./seed
COPY nginx.conf start.sh ./
RUN useradd -m -u 1000 user && chmod +x start.sh
USER user
ENV HOME=/home/user \
    DATABASE_URL=sqlite:////home/user/data/avia.db \
    STORAGE_DIR=/home/user/data/files \
    DETECTOR_SPEC=maskrcnn:/app/model/model.pt \
    BENCHMARKS_PATH=/app/artifacts/benchmarks.json \
    CORS_ORIGINS=https://abhishek1402-avia.hf.space \
    TRUST_PROXY=1
EXPOSE 7860
CMD ["./start.sh"]
