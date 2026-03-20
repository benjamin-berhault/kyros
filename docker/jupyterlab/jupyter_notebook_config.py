import os

# Get the port from the environment, default to 5005 if not set
kyros_port = os.environ.get('KYROS_PORT', '5005')

# Allow requests from the web app running on the dynamic port
c.ServerApp.allow_origin = f'http://localhost:{kyros_port}'
c.ServerApp.allow_credentials = True

# WebSocket settings
c.ServerApp.websocket_ping_timeout = 30     # In seconds
c.ServerApp.websocket_max_message_size = 10485760  # Set max message size

# Tornado settings for headers and XSRF protection
c.ServerApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': f"frame-ancestors 'self' http://localhost:{kyros_port};"
    },
    'xsrf_cookies': False
}
