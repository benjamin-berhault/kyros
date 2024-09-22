from flask import Flask, render_template, make_response, Response, stream_with_context, request, redirect, jsonify
import requests
from requests.exceptions import ConnectionError
import datetime
import yaml
import psutil
import platform
import os
import subprocess

app = Flask(__name__)

# Configuration for Portainer API
PORTAINER_HOST = "http://portainer:9000"  # Or your host's actual IP address
USERNAME = "admin"  # Replace with your Portainer username
PASSWORD = "your_password"  # Replace with your Portainer password
ENDPOINT_ID = "2"  # Replace with the correct endpoint ID for Docker

# Spark Master URL
SPARK_MASTER_URL = 'http://spark-master:8080/json'

def load_menu_config():
    with open('menu.yml', 'r') as file:
        return yaml.safe_load(file)

menu_data = load_menu_config()


# Function to get detailed CPU information
def get_cpu_info():
    cpu_freq = psutil.cpu_freq()  # Get CPU frequency
    cpu_info = {
        'cpu_physical_cores': psutil.cpu_count(logical=False),  # Physical cores
        'cpu_logical_cores': psutil.cpu_count(logical=True),    # Logical cores
        'cpu_base_speed': cpu_freq.max if cpu_freq else 'N/A',  # Base speed
        'cpu_current_speed': cpu_freq.current if cpu_freq else 'N/A',  # Current speed
    }
    return cpu_info


# Function to get detailed Memory information
def get_memory_info():
    memory = psutil.virtual_memory()  # Get virtual memory details
    # Get the memory installed by checking system files or using platform-specific methods
    if platform.system() == 'Windows':
        mem_installed = memory.total / (1024 ** 3)  # Total installed memory in GB


    return {
        'memory_total': memory.total / (1024 ** 3),  # Total memory in GB
        'memory_used': memory.used / (1024 ** 3),    # Used memory in GB
        'memory_percent': memory.percent,            # Memory usage percentage
    }

# Function to get disk space information
def get_disk_info():
    disk = psutil.disk_usage('/')  # Get disk usage details for root directory
    return {
        'disk_total': disk.total / (1024 ** 3),   # Total disk space in GB
        'disk_used': disk.used / (1024 ** 3),     # Used disk space in GB
        'disk_free': disk.free / (1024 ** 3),     # Free disk space in GB
        'disk_percent': disk.percent              # Percentage of disk space used
    }

# Route to get live system resource data (CPU and Memory)
@app.route('/stats')
def get_system_stats():
    memory_info = get_memory_info()
    cpu_info = get_cpu_info()
    disk_info = get_disk_info()

    return jsonify({
        'cpu_info': cpu_info,
        'memory_info': memory_info,
        'disk_info': disk_info
    })


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
    return render_template('base.html', content_url='/home', menu=menu_data)

# @app.route('/home')
# def home():
#     # Get the JWT token for Portainer API
#     token = get_portainer_token()
#     print("## get_portainer_token() token ",token)
    
#     # Get the list of all containers and their status from Portainer API
#     containers = get_container_statuses(token)
#     print("## get_portainer_token() containers ",token)
    
#     # Prepare container data
#     container_info = prepare_container_info(containers)
#     print("## get_portainer_token() container_info ",token)
    
#     # Render the template and pass the container information
#     return render_template('containers.html', containers=container_info, state_color=state_color)

@app.route('/home')
def home():
    try:
        # Get the JWT token for Portainer API
        token = get_portainer_token()

        # Get the list of all containers and their status from Portainer API
        containers = get_container_statuses(token)

        # Prepare container data
        container_info = prepare_container_info(containers)
        
        # Debug: Print the container data
        print(container_info)

        # Debug: Print status color for the first container
        if container_info:
            print(state_color(container_info[0]['status']))

        # Render the template and pass the container information
        return render_template('containers.html', containers=container_info, state_color=state_color)

    except ConnectionError:
        # Portainer is not available, return a custom error page or message
        return render_template('error.html', message="Portainer is not available. Please try again later."), 503

    except Exception as e:
        # Log any other unexpected exceptions and return an internal server error
        print(f"Unexpected error: {e}")
        return render_template('error.html', message="An unexpected error occurred. Please try again later."), 500


@app.route('/cloudbeaver')
def cloudbeaver():
    # Embed CloudBeaver inside an iframe
    return render_template('base.html', content_url='http://localhost:8978', menu=menu_data)

@app.route('/codeserver')
def codeserver():
    # Embed CloudBeaver inside an iframe
    return render_template('base.html', content_url='http://localhost:8083', menu=menu_data)

@app.route('/jupyterlab')
def jupyterlab():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:8888', menu=menu_data)

@app.route('/minio')
def minio():
    return render_template('base.html', content_url='http://localhost:9003', menu=menu_data)

@app.route('/dagster')
def dagster():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:3000', menu=menu_data)
    
# @app.route('/spark')
# def spark():
#     # Define the Spark Master and Worker URLs
#     spark_services = [
#         {"name": "Spark Worker 1", "url": "http://localhost:8081"},
#         {"name": "Spark Worker 2", "url": "http://localhost:8082"}
#     ]
    
#     # Pass the list of services to the template
#     return render_template('spark.html', services=spark_services)

# @app.route('/spark')
# def spark():
#     # Pass the list of services to the template
#     return render_template('spark.html')


@app.route('/spark')
def spark():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='/spark-iframe', menu=menu_data)

@app.route('/spark-iframe')
def spark_iframe():
    try:
        # Fetch the Spark Master info from the API
        response = requests.get(SPARK_MASTER_URL)
        response.raise_for_status()  # Ensure the request was successful
        spark_data = response.json()  # Parse the JSON response

        # Pass the Spark data to the template that will be loaded in an iframe
        return render_template('spark.html', spark=spark_data)

    except requests.exceptions.RequestException as e:
        # Handle connection errors
        return f"Error fetching Spark data: {e}", 500

@app.route('/portainer')
def portainer():
    # Embed JupyterLab inside an iframe
    return render_template('base.html', content_url='http://localhost:9000', menu=menu_data)

@app.route('/not_found')
def not_found():
    return render_template('404.html'), 404  # Render template with status code 404

# Add more routes for other components as needed
# e.g., Spark UI, MinIO, etc.

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

