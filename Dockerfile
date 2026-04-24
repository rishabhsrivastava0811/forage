FROM python:3.11-slim AS base

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .
RUN mkdir -p /data

ENV FORAGE_DATA_DIR=/data
EXPOSE 3000

ENTRYPOINT ["forage"]
CMD ["start"]

# ============================================================
# GPU variant — use this if you have NVIDIA GPUs:
#   docker build --target gpu -t forage-gpu .
#   docker run --gpus all forage-gpu
# ============================================================
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04 AS gpu

RUN apt-get update && apt-get install -y python3.11 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[local-models]"

COPY . .
RUN mkdir -p /data

ENV FORAGE_DATA_DIR=/data
EXPOSE 3000

ENTRYPOINT ["forage"]
CMD ["start"]
