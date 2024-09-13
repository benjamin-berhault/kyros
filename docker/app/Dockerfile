ARG IMAGE=python:3.9-slim
FROM ${IMAGE}


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
