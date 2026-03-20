# Use an official Python runtime as a parent image
ARG IMAGE=python:3.10-slim
FROM ${IMAGE}

# Set the working directory to /app
WORKDIR /app

# Install MkDocs and Material theme
RUN pip install mkdocs-material mkdocs-glightbox

# Copy the current directory contents into the container at /app
COPY ./mkdocs.yml /app/mkdocs.yml
COPY ./docs/css /app/docs/css
COPY ./docs/js /app/docs/js

# Expose port 8000
EXPOSE 8000

# Define the default command to run MkDocs server
# ENTRYPOINT ["tail", "-f", "/dev/null"]
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
