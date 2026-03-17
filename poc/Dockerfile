FROM python:3.9-slim
WORKDIR /app

# Install Docker CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5003
CMD ["uvicorn", "app.main:asgi_app", "--host", "0.0.0.0", "--port", "5003"]
