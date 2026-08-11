FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libzbar0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY servers ./servers

RUN pip install --no-cache-dir .

ENV MCP_SERVERS=all \
    MCP_TRANSPORT=http \
    HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

CMD ["python", "-m", "src.gateway"]
