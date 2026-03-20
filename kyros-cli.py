#!/usr/bin/env python3
"""
Kyros CLI - Deploy the right architecture at the right time

Interactive component selection with GitLab-style build/deploy logs.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
except ImportError:
    print("Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

# Component definitions with metadata
COMPONENTS = {
    "POSTGRES": {"name": "PostgreSQL", "level": 1, "desc": "Relational database", "port": 5432},
    "DAGSTER": {"name": "Dagster", "level": 1, "desc": "Orchestration & pipelines", "port": 3000},
    "SUPERSET": {"name": "Superset", "level": 1, "desc": "BI & dashboards", "port": 8088},
    "DBT": {"name": "dbt", "level": 0, "desc": "SQL transformations", "port": None},
    "MINIO": {"name": "MinIO", "level": 2, "desc": "Object storage (S3)", "port": 9001},
    "JUPYTERLAB": {"name": "JupyterLab", "level": 2, "desc": "Notebooks & analysis", "port": 8888},
    "TRINO": {"name": "Trino", "level": 3, "desc": "Federated SQL queries", "port": 8082},
    "KAFKA": {"name": "Kafka", "level": 4, "desc": "Event streaming", "port": 9092},
    "FLINK": {"name": "Flink", "level": 4, "desc": "Stream processing", "port": 8081},
    "GRAFANA": {"name": "Grafana", "level": 2, "desc": "Monitoring dashboards", "port": 3002},
    "LOKI": {"name": "Loki", "level": 2, "desc": "Log aggregation", "port": 3100},
    "PROMTAIL": {"name": "Promtail", "level": 2, "desc": "Log collector", "port": None},
    "CLOUDBEAVER": {"name": "CloudBeaver", "level": 1, "desc": "Database UI", "port": 8978},
    "CODE_SERVER": {"name": "Code Server", "level": 2, "desc": "VS Code in browser", "port": 8083},
    "PORTAINER": {"name": "Portainer", "level": 1, "desc": "Container management", "port": 9000},
    "KYROS": {"name": "Kyros Dashboard", "level": 1, "desc": "Platform control panel", "port": 5000},
}

LEVELS = {
    0: {"name": "Local", "desc": "DuckDB + dbt", "cost": "$0", "data": "< 50 GB"},
    1: {"name": "Team", "desc": "+ PostgreSQL + Dagster + Superset", "cost": "$20-100", "data": "< 500 GB"},
    2: {"name": "Data Lake", "desc": "+ MinIO + Delta Lake", "cost": "$50-150", "data": "< 1 TB"},
    3: {"name": "Distributed", "desc": "+ Spark + Trino", "cost": "$150-500", "data": "1+ TB"},
    4: {"name": "Enterprise", "desc": "+ Flink + Kafka + SSO", "cost": "$500+", "data": "Any"},
}


def show_banner():
    banner = """
    ██╗  ██╗██╗   ██╗██████╗  ██████╗ ███████╗
    ██║ ██╔╝╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔════╝
    █████╔╝  ╚████╔╝ ██████╔╝██║   ██║███████╗
    ██╔═██╗   ╚██╔╝  ██╔══██╗██║   ██║╚════██║
    ██║  ██╗   ██║   ██║  ██║╚██████╔╝███████║
    ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    """
    console.print(Panel(banner, title="[bold blue]Data Engineering at the Right Scale[/]",
                        subtitle="Right tool • Right time • Right cost"))


def show_levels():
    table = Table(title="Architecture Levels", show_header=True, header_style="bold magenta")
    table.add_column("Level", style="cyan", width=8)
    table.add_column("Name", style="green")
    table.add_column("Stack", style="white")
    table.add_column("Data Size", style="yellow")
    table.add_column("Cost/Month", style="red")

    for level, info in LEVELS.items():
        table.add_row(str(level), info["name"], info["desc"], info["data"], info["cost"])

    console.print(table)


def show_components(selected=None):
    if selected is None:
        selected = set()

    table = Table(title="Available Components", show_header=True, header_style="bold magenta")
    table.add_column("", width=3)
    table.add_column("Component", style="green")
    table.add_column("Description", style="white")
    table.add_column("Level", style="cyan")
    table.add_column("Port", style="yellow")

    for key, comp in COMPONENTS.items():
        check = "[green]✓[/]" if key in selected else "[ ]"
        level_str = f"L{comp['level']}+"
        port_str = str(comp['port']) if comp['port'] else "-"
        table.add_row(check, comp['name'], comp['desc'], level_str, port_str)

    console.print(table)


def select_level():
    show_levels()
    console.print()

    choice = Prompt.ask(
        "[bold]Select a level[/] (or 'c' for custom)",
        choices=["0", "1", "2", "3", "4", "c"],
        default="1"
    )

    if choice == "c":
        return None, custom_selection()

    level = int(choice)
    # Get components for this level
    selected = {k for k, v in COMPONENTS.items() if v["level"] <= level}
    return level, selected


def custom_selection():
    selected = set()
    show_components(selected)

    console.print("\n[bold]Enter component names to toggle (comma-separated), or 'done' to finish:[/]")
    console.print("[dim]Available: " + ", ".join(COMPONENTS.keys()) + "[/]")

    while True:
        choice = Prompt.ask("Toggle").strip().upper()

        if choice == "DONE":
            break

        for comp in choice.split(","):
            comp = comp.strip()
            if comp in COMPONENTS:
                if comp in selected:
                    selected.remove(comp)
                else:
                    selected.add(comp)

        console.clear()
        show_components(selected)

    return selected


def generate_env(selected, workers=0):
    """Generate .env content from selected components."""
    lines = ["# Generated by Kyros CLI", ""]

    all_components = list(COMPONENTS.keys())
    for key in all_components:
        value = "true" if key in selected else "false"
        lines.append(f"INCLUDE_{key}={value}")

    lines.extend([
        "",
        f"WORKERS={workers}",
        "",
        "SPARK_MASTER_HOST=spark-master",
        "SPARK_MASTER_PORT=7077",
        "SPARK_WORKER_MEMORY=2G",
        "SPARK_EXECUTOR_MEMORY=2G",
        "SPARK_WORKER_CORES=2",
        "SPARK_EXECUTOR_CORES=2",
        "",
        "POSTGRES_USER=kyros",
        "POSTGRES_PASSWORD=kyros_dev",
        "",
        "SUPERSET_ADMIN=admin",
        "SUPERSET_PASSWORD=admin",
        "SUPERSET_SECRET_KEY=ChangeMeToARandomString",
        "",
        "DAGSTER_WORKSPACE=kyros",
    ])

    return "\n".join(lines)


def run_command(cmd, title):
    """Run command with GitLab-style output."""
    console.print(Panel(f"[bold cyan]$ {cmd}[/]", title=title, border_style="blue"))

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output_lines = []
    for line in process.stdout:
        line = line.rstrip()
        output_lines.append(line)

        # Color code output
        if "error" in line.lower() or "failed" in line.lower():
            console.print(f"  [red]{line}[/]")
        elif "warning" in line.lower():
            console.print(f"  [yellow]{line}[/]")
        elif "success" in line.lower() or "done" in line.lower() or "✓" in line:
            console.print(f"  [green]{line}[/]")
        elif line.startswith("#") or line.startswith("=>"):
            console.print(f"  [dim]{line}[/]")
        else:
            console.print(f"  {line}")

    process.wait()

    if process.returncode == 0:
        console.print(f"[bold green]✓ {title} completed successfully[/]\n")
    else:
        console.print(f"[bold red]✗ {title} failed (exit code {process.returncode})[/]\n")

    return process.returncode == 0


def deploy(selected, workers=0):
    """Generate config and deploy selected components."""
    kyros_dir = Path(__file__).parent

    # Step 1: Generate .env
    console.print(Panel("[bold]Step 1/3: Generating configuration[/]", border_style="cyan"))
    env_content = generate_env(selected, workers)
    env_path = kyros_dir / ".env"
    env_path.write_text(env_content)
    console.print(f"[green]✓ Generated .env with {len(selected)} components[/]\n")

    # Step 2: Generate docker-compose.yml using Python module
    console.print(Panel("[bold]Step 2/3: Generating docker-compose.yml[/]", border_style="cyan"))
    try:
        from generate_compose import generate_docker_compose, load_env_file
        env_vars = load_env_file(env_path)
        generate_docker_compose(kyros_dir, env_vars)
        console.print("[green]✓ Generated docker-compose.yml[/]\n")
    except Exception as e:
        console.print(f"[red]✗ Failed to generate docker-compose.yml: {e}[/]\n")
        return False

    # Step 3: Build and start
    console.print(Panel("[bold]Step 3/3: Building and starting services[/]", border_style="cyan"))
    success = run_command(
        f"cd {kyros_dir} && docker compose up -d --build",
        "Docker Compose Build & Start"
    )

    if success:
        show_access_urls(selected)

    return success


def show_access_urls(selected):
    """Show URLs for running services."""
    table = Table(title="[bold green]Services Running[/]", show_header=True)
    table.add_column("Service", style="cyan")
    table.add_column("URL", style="green")

    for key in selected:
        comp = COMPONENTS.get(key)
        if comp and comp["port"]:
            table.add_row(comp["name"], f"http://localhost:{comp['port']}")

    console.print()
    console.print(table)
    console.print()


def stop_all():
    """Stop all services."""
    kyros_dir = Path(__file__).parent
    run_command(f"cd {kyros_dir} && docker compose down", "Stopping all services")


def show_status():
    """Show running containers."""
    kyros_dir = Path(__file__).parent
    run_command(f"cd {kyros_dir} && docker compose ps", "Container Status")


def main():
    show_banner()
    console.print()

    action = Prompt.ask(
        "[bold]What would you like to do?[/]",
        choices=["deploy", "stop", "status", "levels", "quit"],
        default="deploy"
    )

    if action == "quit":
        return

    if action == "stop":
        if Confirm.ask("Stop all running services?"):
            stop_all()
        return

    if action == "status":
        show_status()
        return

    if action == "levels":
        show_levels()
        console.print("\n[dim]Use 'deploy' to select and deploy a level[/]")
        return

    # Deploy flow
    level, selected = select_level()

    console.print()
    show_components(selected)
    console.print()

    # Ask for Spark workers if level >= 3
    workers = 0
    if level and level >= 3:
        workers = int(Prompt.ask("Number of Spark workers", default="2"))
    elif "TRINO" in selected or "KAFKA" in selected:
        workers = int(Prompt.ask("Number of Spark workers", default="2"))

    if Confirm.ask(f"\n[bold]Deploy {len(selected)} components?[/]"):
        console.print()
        deploy(selected, workers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/]")
