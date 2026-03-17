from flask import session, Blueprint, render_template, request, redirect, url_for, jsonify
from .socketio import socketio
import subprocess
import threading

main = Blueprint('main', __name__)

@main.route("/emit_test", methods=["GET", "POST"])
def emit_test():
    socketio.emit("log", {"message": "Test message"}, namespace="/deploy")
    return jsonify({"status": "success", "message": "Emit test successful!"})



@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Collect selected options
        form_data = request.form.to_dict()

        # Extract only selected options (i.e., values that are 'true')
        summary = [
            key.replace("INCLUDE_", "").replace("_", " ").title()
            for key, value in form_data.items()
            if value.lower() == "true"
        ]
        
        # Store the summary in the session
        session['summary'] = summary
        
        # Redirect to the summary route
        return redirect(url_for("main.summary"))
    
    return render_template("index.html", title="Configuration")


@main.route("/summary", methods=["GET"])
def summary():
    # Retrieve the summary from the session
    summary = session.get('summary', [])
    
    # Render the summary page
    return render_template("summary.html", summary=summary)


def run_command(cmd, namespace):
    """Run a shell command and emit real-time logs to the client."""
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        for line in process.stdout:
            line = line.strip()
            socketio.emit('log', {'message': line}, namespace=namespace)

        for line in process.stderr:
            line = line.strip()

            # Categorize messages based on common Docker Compose patterns
            if any(keyword in line for keyword in ["level=warning", "Creating", "Starting", "Started"]):
                socketio.emit('log', {'message': f"WARNING: {line}"}, namespace=namespace)
            elif "orphan containers" in line:
                socketio.emit('log', {'message': f"NOTICE: {line}"}, namespace=namespace)
            else:
                socketio.emit('log', {'message': f"ERROR: {line}"}, namespace=namespace)

    except Exception as e:
        # Log any unexpected issues during command execution
        socketio.emit('log', {'message': f"ERROR: Exception while running command: {str(e)}"}, namespace=namespace)

    process.wait()


def execute_workflow():
    """Execute the workflow and stream logs."""
    commands = [
        "docker ps -q | xargs -r docker stop && docker ps -aq | xargs -r docker rm",
        "cd .. && docker compose -f docker-compose-registry.yml up --build --no-deps --remove-orphans -d",
        "cd .. && ./tools/pull-image-locally.sh",
        "cd .. && ./tools/pull-jars-locally.sh",
        "cd .. && docker compose -f docker-compose.yml up --build --no-deps --remove-orphans -d",
    ]
    namespace = '/deploy'
    try:
        for cmd in commands:
            socketio.emit('log', {'message': f"Running: {cmd}"}, namespace=namespace)
            run_command(cmd, namespace)
        socketio.emit('log', {'message': "Deployment successful"}, namespace=namespace)
    except Exception as e:
        socketio.emit('log', {'message': f"Deployment failed: {str(e)}"}, namespace=namespace)



@socketio.on('start_workflow', namespace='/deploy')
def start_workflow():
    """Start the workflow in a separate thread."""
    threading.Thread(target=execute_workflow).start()

def summarize_configuration(config):
    """Summarize the selected configuration."""
    summary = []

    # Example of adding configuration details
    if config.get("INCLUDE_MKDOCS") == "true":
        summary.append("MKDocs included.")
    if config.get("INCLUDE_JUPYTERLAB") == "true":
        summary.append("JupyterLab included.")
    # Add more configuration summaries as needed

    return summary

@main.route('/logs')
def logs():
    try:
        with open('app.log', 'r') as log_file:
            logs = log_file.read()
    except FileNotFoundError:
        logs = "[ERROR] Log file not found."
    return render_template('logs.html', title="Logs", logs=logs)


@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="404 Error"), 404

@main.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html', title="Server Error"), 500