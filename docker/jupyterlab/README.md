To run `dbt` with both Parquet files and PostgreSQL, you need to install and configure the appropriate dbt plugins. For PostgreSQL, you can use the `dbt-postgres` adapter, and for working with Parquet files, you can use the `dbt-spark` adapter with Spark's `Hadoop` interface. Here’s how you can modify your Dockerfile to support both:

### Key Additions:
1. **dbt-core**: Core package for dbt.
2. **dbt-postgres**: Adapter for connecting dbt to PostgreSQL databases.
3. **dbt-spark[PySpark]**: Adapter for connecting dbt to Spark, allowing it to work with Parquet files through the Hadoop interface.

### Setting Up dbt Profiles:
To run dbt with both PostgreSQL and Parquet files, you need to set up the appropriate configurations in your `profiles.yml`. Here's an example:

#### profiles.yml
```yaml
default:
  target: dev
  outputs:
    dev:
      type: postgres
      host: your-postgres-host
      user: your-username
      password: your-password
      dbname: your-database
      schema: your-schema
      threads: 4
      port: 5432

spark_profile:
  target: dev
  outputs:
    dev:
      type: spark
      method: 'hadoop'
      schema: your_spark_schema
      host: your-spark-host
      port: 10001
      connection_timeout: 30
      # Customize according to your Parquet setup
```

### Running dbt Commands in Jupyter:
You can run `dbt` commands directly within your Jupyter notebooks:

```python
# For PostgreSQL
!dbt run --profiles-dir path/to/profiles.yml --project-dir path/to/project

# For Spark (Parquet)
!dbt run --profiles-dir path/to/profiles.yml --profile spark_profile --project-dir path/to/project
```

Maybe also try:

```python
!dbt run
!dbt test
```

With these configurations, your Jupyter environment will be ready to run `dbt` scripts for both PostgreSQL and Parquet file-based data warehouses.