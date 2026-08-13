FROM python:3.12-slim AS builder

WORKDIR /app
RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN python -m pip install --no-cache-dir --prefix=/install ".[web]"

FROM python:3.12-slim

COPY --from=builder /install /usr/local

USER 65534
EXPOSE 8501
CMD ["ai-governance-assistant"]
