import subprocess
from dagster import op, job, repository, Field, Shape

# Utility function to execute commands
def run_command(command, context):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        context.log.info(result.stdout)
    except subprocess.CalledProcessError as e:
        context.log.error(f"Command failed: {e.stderr}")
        raise

# Operations
@op(config_schema={"script_path": Field(str)}, description="Runs a PyFlink job using the specified script.")
def run_pyflink_job(context):
    script_path = context.op_config["script_path"]
    command = ["flink", "run", "-m", "jobmanager:8081", script_path]
    run_command(command, context)

@op(config_schema={"script_path": Field(str)}, description="Triggers a custom Flink Python job using the specified script.")
def trigger_flink_python_job(context):
    script_path = context.op_config["script_path"]
    command = ["flink", "run", "-m", "jobmanager:8081", "python", script_path]
    run_command(command, context)

# Jobs
@job(description="Runs the PyFlink job using a configured script path.")
def flink_job():
    run_pyflink_job()

@job(description="Triggers the execution of a custom Flink Python job using a configured script path.")
def flink_python_job():
    trigger_flink_python_job()

# Combined Pipeline Job
@job(description="Executes all defined operations in sequence.")
def flink_pipeline():
    run_pyflink_job()
    trigger_flink_python_job()

# Repository
@repository
def my_repository():
    return [flink_job, flink_python_job, flink_pipeline]
