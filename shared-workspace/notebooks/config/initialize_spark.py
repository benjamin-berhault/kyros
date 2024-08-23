from pyspark.sql import SparkSession
import os

# Define constants
DATA_FOLDER = "../../data"  # Constant for the repository path

try:
    from delta import configure_spark_with_delta_pip, DeltaTable
    DELTA_AVAILABLE = True
except ImportError:
    DELTA_AVAILABLE = False

def initialize_spark(use_delta=False):
    # Get the absolute path of the currently running script
    current_file_path = os.path.abspath(__file__)
    # Print the path
    print(f"initialize_spark() executed from: {current_file_path}")
    print(f"DATA_FOLDER being defined as: {DATA_FOLDER}")

    builder = (SparkSession.builder
               .appName("read-delta-table")
               .config("spark.ui.port", "4040")
               .master("spark://spark-master:7077")
               .config("spark.executor.memory", "512m"))
    
    if use_delta and DELTA_AVAILABLE:
        # Add Delta Lake specific configurations if Delta is available and requested
        builder = (builder.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                          .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))
        
        # Initialize Spark session with Delta support
        spark = configure_spark_with_delta_pip(builder).getOrCreate()
        delta_table_path = f"{DATA_FOLDER}/delta_lake/netflix_titles"
        print("Delta Lake support is enabled.")
        return spark, delta_table_path
    else:
        # Initialize Spark session without Delta support
        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        print("Delta Lake support is not enabled.")
        return spark

# Example usage
# spark, delta_table_path = initialize_spark(use_delta=True)  # Set use_delta=False to run without Delta Lake
