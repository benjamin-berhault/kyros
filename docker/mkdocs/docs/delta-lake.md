# Manage Data in a Delta Format Through a Database Management Tool

Connect with your SQL client of choice. The following steps are applicable with
[DBeaver](https://dbeaver.io/download).

## Connection 

Open your database management tools (e.g. DBeaver)

Create a new connection (`jdbc:trino://localhost:8080`)
* Database connection type: Trino
* Connect by: Host
* Host: localhost
* Port: 8080
* Username: trino
* Password:

From here you can follow along with the demo, or try your own SQL queries. The
following queries are used in the demo.

Verify that the catalog is available:

```sql
SHOW CATALOGS;
```

Check if there are any schemas:

```sql
SHOW SCHEMAS FROM delta;
```

Let's create a new schema:

```sql
CREATE SCHEMA delta.myschema WITH (location='s3a://claudiustestbucket/myschema');
```

Create a table, insert some records, and then verify:

```sql
CREATE TABLE delta.myschema.mytable (name varchar, id integer);
INSERT INTO delta.myschema.mytable VALUES ( 'John', 1), ('Jane', 2);
SELECT * FROM delta.myschema.mytable;
```

Run a query to get more data and insert it into a new table:

```sql
CREATE TABLE delta.myschema.myothertable AS
  SELECT * FROM delta.myschema.mytable;

SELECT * FROM delta.myschema.myothertable ;
```

Now for some data manipulation:

```sql
UPDATE delta.myschema.myothertable set name='Jonathan' where id=1;
SELECT * FROM delta.myschema.myothertable ;
DELETE FROM delta.myschema.myothertable where id=2;
SELECT * FROM delta.myschema.myothertable ;
```

And finally, lets clean up:

```sql
ALTER TABLE delta.myschema.mytable EXECUTE optimize(file_size_threshold => '10MB');
ANALYZE delta.myschema.myothertable;
DROP TABLE delta.myschema.myothertable ;
DROP TABLE delta.myschema.mytable ;
DROP SCHEMA delta.myschema;
```