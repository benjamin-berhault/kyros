ARG IMAGE=python:3.9-slim
FROM ${IMAGE}

RUN apt-get update && apt-get install -y libpq-dev gcc wget

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

ARG POSTGRES_USER
ARG POSTGRES_PASSWORD

ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD

WORKDIR /home/generator

COPY . .

RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

CMD ["python", "generate.py"]
