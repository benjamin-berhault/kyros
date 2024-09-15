import subprocess
from dagster import op, job

@op
def hello_world(context):
    context.log.info("Hello, World!")

@op
def run_pyflink_job(context):
    command = [
        "flink", 
        "run", 
        "-m", "jobmanager:8081", 
        "/opt/pyflink/word_count.py"
    ]
    result = subprocess.run(command, capture_output=True, text=True)

    context.log.info(result.stdout)
    if result.returncode != 0:
        raise Exception(f"Flink job failed: {result.stderr}")

@op
def trigger_flink_python_job(context):
    # Command to execute the Python Flink job inside the Flink JobManager container
    command = [
        "flink", 
        "run", 
        "-m", "jobmanager:8081", 
        "python", "/opt/flink/jobs/flink_kafka_to_parquet.py"
    ]
    
    try:
        subprocess.run(command, check=True)
        context.log.info("Flink Python job executed successfully.")
    except subprocess.CalledProcessError as e:
        context.log.error(f"Failed to execute Flink Python job: {e}")
        raise

@job
def hello_world_job():
    hello_world()

@job
def flink_job():
    run_pyflink_job()

@job
def flink_python_job():
    trigger_flink_python_job()

# dbt
@op
def run_dbt(context):
    context.log.info("Running dbt models...")
    os.system("docker-compose run dbt dbt run --profiles-dir ./profiles --target prod")

@op
def test_dbt(context):
    context.log.info("Testing dbt models...")
    os.system("docker-compose run dbt dbt test --profiles-dir ./profiles --target prod")

@job
def dbt_pipeline():
    run_dbt()
    test_dbt()