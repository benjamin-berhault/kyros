from flask import Flask, render_template, make_response, Response, stream_with_context, request, redirect
import requests
import datetime

app = Flask(__name__)

# Configuration for Portainer API
PORTAINER_HOST = "http://portainer:9000"  # Or your host's actual IP address
USERNAME = "admin"  # Replace with your Portainer username
PASSWORD = "your_password"  # Replace with your Portainer password
ENDPOINT_ID = "2"  # Replace with the correct endpoint ID for Docker


# Authenticate with Portainer API to get the JWT token
def get_portainer_token():
    url = f"{PORTAINER_HOST}/api/auth"
    headers = {"Content-Type": "application/json"}
    data = {"Username": USERNAME, "Password": PASSWORD}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json().get("jwt")
    else:
        raise Exception("Failed to authenticate with Portainer API")

# Get the list of containers and their statuses from Portainer
def get_container_statuses(token):
    url = f"{PORTAINER_HOST}/api/endpoints/{ENDPOINT_ID}/docker/containers/json?all=true"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve container statuses")

# Format container data
def prepare_container_info(containers):
    container_info = []
    for container in containers:
        created_time = datetime.datetime.utcfromtimestamp(container["Created"]).strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle the case where network may vary or not exist
        networks = container["NetworkSettings"].get("Networks", {})
        ip_address = "N/A"
        if networks:
            # Get the first available network's IP address
            for network_name, network_data in networks.items():
                ip_address = network_data.get("IPAddress", "N/A")
                break  # Exit after the first network (you can adjust if needed)

        ports = container.get("Ports", [])
        published_ports = ', '.join(
            [f"{p.get('IP', 'N/A')}: {p.get('PublicPort', 'N/A')}" for p in ports if "PublicPort" in p]
        )
        
        container_info.append({
            'name': container["Names"][0].strip("/"),
            'status': container["State"],
            'image': container["Image"],
            'created': created_time,
            'ip_address': ip_address,
            'published_ports': published_ports
        })
    return container_info

# Determine the text color for container state (Portainer-like)
def state_color(state):
    if state == "running":
        return "text-success"
    elif state == "exited":
        return "text-danger"
    elif state == "paused":
        return "text-warning"
    elif state == "created":
        return "text-primary"
    else:
        return "text-secondary"

@app.route('/')
def route():
    # Home page rendering base.html with dynamic content URL
    return render_template('base.html', content_url='/home')

@app.route('/home')
def home():
    # Get the JWT token for Portainer API
    token = get_portainer_token()
    
    # Get the list of all containers and their status from Portainer API
    containers = get_container_statuses(token)
    
    # Prepare container data
    container_info = prepare_container_info(containers)
    
    # Render the template and pass the container information
    return render_template('containers.html', containers=container_info, state_color=state_color)

@app.route('/cloudbeaver')
def cloudbeaver():
    # Embed CloudBeaver inside an iframe
    return render_template('base.html', content_url='http://localhost:8978')

@app.route('/codeserver')
def codeserver():
    # Embed CloudBeaver inside an iframe
    return render_template('base.html', content_url='http://localhost:8083')

@app.route('/jupyterlab')
def jupyterlab():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:8888')

@app.route('/minio')
def minio():
    return render_template('base.html', content_url='http://localhost:9003')

@app.route('/dagster')
def dagster():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:3000')
    
@app.route('/spark')
def spark():
    # Define the Spark Master and Worker URLs
    spark_services = [
        {"name": "Spark Master", "url": "http://localhost:8080"},
        {"name": "Spark Worker 1", "url": "http://localhost:8081"},
        {"name": "Spark Worker 2", "url": "http://localhost:8082"}
    ]
    
    # Pass the list of services to the template
    return render_template('spark.html', services=spark_services)

@app.route('/portainer')
def portainer():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:9000')

@app.route('/not_found')
def not_found():
    return render_template('404.html'), 404  # Render template with status code 404

# Add more routes for other components as needed
# e.g., Spark UI, MinIO, etc.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

