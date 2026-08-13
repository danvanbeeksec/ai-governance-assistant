FROM python:3.12-slim

WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir ".[web]"

USER 65534
EXPOSE 8501
CMD ["ai-governance-assistant"]
