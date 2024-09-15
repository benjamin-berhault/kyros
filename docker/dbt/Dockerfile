ARG IMAGE=ghcr.io/dbt-labs/dbt-core:1.5.latest
FROM ${IMAGE}

# Optional: Set the working directory
WORKDIR /usr/app/dbt

# Install PostgreSQL and Redshift adapters
RUN pip install dbt-postgres dbt-spark

# Copy your dbt project to the container
COPY ./dbt_project /usr/app/dbt
