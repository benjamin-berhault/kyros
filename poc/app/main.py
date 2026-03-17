import os
import subprocess
import threading
from pathlib import Path

import socketio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create FastAPI app
app = FastAPI(title="Kyros Deployment")

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Static files and templates
app_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=app_dir / "static"), name="static")
templates = Jinja2Templates(directory=app_dir / "templates")

# Session storage (simple in-memory for demo)
sessions = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Configuration"})


@app.post("/", response_class=HTMLResponse)
async def index_post(request: Request):
    form_data = await request.form()

    # Extract selected options
    summary = [
        key.replace("INCLUDE_", "").replace("_", " ").title()
        for key, value in form_data.items()
        if str(value).lower() == "true"
    ]

    # Store in session (using client IP as simple key)
    client_id = request.client.host
    sessions[client_id] = {"summary": summary, "form_data": dict(form_data)}

    return RedirectResponse(url="/summary", status_code=303)


@app.get("/summary", response_class=HTMLResponse)
async def summary(request: Request):
    client_id = request.client.host
    session_data = sessions.get(client_id, {})
    summary = session_data.get("summary", [])

    return templates.TemplateResponse("summary.html", {
        "request": request,
        "summary": summary,
        "title": "Summary"
    })


@app.get("/logs", response_class=HTMLResponse)
async def logs(request: Request):
    try:
        with open('logs/app.log', 'r') as log_file:
            log_content = log_file.read()
    except FileNotFoundError:
        log_content = "[ERROR] Log file not found."

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": log_content,
        "title": "Logs"
    })


# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.on('start_workflow')
async def start_workflow(sid):
    """Start the deployment workflow in a background thread."""
    threading.Thread(target=execute_workflow_sync, args=(sid,)).start()


def run_command_sync(cmd: str, sid: str):
    """Run a shell command and emit real-time logs."""
    import asyncio

    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    loop = asyncio.new_event_loop()

    try:
        for line in process.stdout:
            line = line.strip()
            loop.run_until_complete(sio.emit('log', {'message': line}, room=sid))

        for line in process.stderr:
            line = line.strip()
            if any(kw in line for kw in ["level=warning", "Creating", "Starting", "Started"]):
                loop.run_until_complete(sio.emit('log', {'message': f"WARNING: {line}"}, room=sid))
            elif "orphan containers" in line:
                loop.run_until_complete(sio.emit('log', {'message': f"NOTICE: {line}"}, room=sid))
            else:
                loop.run_until_complete(sio.emit('log', {'message': f"ERROR: {line}"}, room=sid))
    except Exception as e:
        loop.run_until_complete(sio.emit('log', {'message': f"ERROR: {str(e)}"}, room=sid))
    finally:
        loop.close()

    process.wait()


def execute_workflow_sync(sid: str):
    """Execute the deployment workflow."""
    import asyncio

    # Use mounted kyros directory when running in container, or relative path otherwise
    kyros_dir = Path("/kyros") if Path("/kyros").exists() else Path(__file__).parent.parent.parent

    commands = [
        f"cd {kyros_dir} && ./generate-docker-compose.sh",
        f"cd {kyros_dir} && docker compose up -d --build",
    ]

    loop = asyncio.new_event_loop()

    try:
        for cmd in commands:
            loop.run_until_complete(sio.emit('log', {'message': f"$ {cmd}"}, room=sid))
            run_command_sync(cmd, sid)

        loop.run_until_complete(sio.emit('log', {'message': "Deployment successful"}, room=sid))
    except Exception as e:
        loop.run_until_complete(sio.emit('log', {'message': f"Deployment failed: {str(e)}"}, room=sid))
    finally:
        loop.close()


# Export the combined ASGI app
asgi_app = socket_app
