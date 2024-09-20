#!/bin/bash

# Start Nginx in the background
service nginx start

# Start Flask (using Gunicorn for production)
exec gunicorn -w 4 -b 127.0.0.1:5000 app:app
