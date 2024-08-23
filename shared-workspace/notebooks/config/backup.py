# This script centralizes the Spark session initialization and configuration settings.
# By defining these configurations in one place, it ensures consistency across multiple 
# notebooks or scripts that rely on Spark. This approach reduces duplication and makes 
# it easier to manage and update configurations, as changes need to be made only in this 
# file rather than in each individual notebook or script.

from delta import configure_spark_with_delta_pip, DeltaTable
from pyspark.sql import SparkSession

def initialize_spark():
    builder = (SparkSession.builder
               # Set the application name for the Spark session
               .appName("read-delta-table")
               .config("spark.ui.port", "4040")
               # Specify the master URL for the Spark cluster
               .master("spark://spark-master:7077")
               # Configure the amount of memory allocated to each Spark executor
               .config("spark.executor.memory", "512m")
               # Enable Delta Lake support by adding the Delta Spark session extension
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               # Set the catalog implementation to Delta for managing metadata and table operations
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))

    # Initialize and configure the Spark session with Delta Lake support
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    # Set the logging level to "ERROR" to minimize log output
    spark.sparkContext.setLogLevel("ERROR")
    spark.sparkContext.setLogLevel("INFO")

    # Define the path within the delta-tables volume
    delta_table_path = "/home/jovyan/work/notebooks/data/delta_lake/netflix_titles"

    # Load the Spark SQL magic extension for running SQL queries with %sparksql
    get_ipython().run_line_magic('load_ext', 'sparksql_magic')
    
    # Set the output limit of Spark SQL queries to 20 rows
    get_ipython().run_line_magic('config', 'SparkSql.limit=20')
    
    # Indicate that the initialize_spark.py module is being imported
    print("notebooks/config/initialize_spark.py has been loaded!")

    return spark, delta_table_path

