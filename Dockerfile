ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE} AS builder

WORKDIR /app
RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
COPY . /app
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM ${PYTHON_IMAGE}

COPY --from=builder /install /usr/local

USER 65534
EXPOSE 8000 8501
CMD ["ai-governance-assistant"]
