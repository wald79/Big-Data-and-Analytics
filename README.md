YouTube Data Pipeline User Guide
Hadoop + Spark + PostgreSQL using Docker
Overview

This project extracts YouTube data using the YouTube Data API, stores the raw JSON in Hadoop HDFS, processes the data using Apache Spark, and loads the cleaned results into PostgreSQL.

Pipeline:

YouTube API → JSON File → HDFS → Spark ETL → PostgreSQL

1. Prerequisites

Install :-

Docker Desktop
Python 3.x
Git (optional)

Verify Docker 

docker --version
docker compose version

2. Start the Big Data Environment

Navigate to the project folder:

cd path/to/project

Start all services :-

docker compose up -d

Verify containers are running:

docker ps

Expected containers:

namenode

datanode

resourcemanager

nodemanager

spark-master

spark-worker

postgres

3. Extract Data from YouTube API

Run the ingestion script :-

python scripts/ingest_youtube_api.py

Expected output 

Data saved successfully

A file named 

youtube_raw.json

will be created in the project directory.

4. Upload JSON File to HDFS

Open the NameNode container:

docker exec -it namenode bash

Create HDFS directories:

hdfs dfs -mkdir -p /data/raw

Exit the container:

exit

Copy the JSON file into the NameNode container(You can do it PowerShell or VScode Terminal):

docker cp youtube_raw.json namenode:/root/    -

Enter the NameNode again:

docker exec -it namenode bash

Upload the file to HDFS:

hdfs dfs -put /root/youtube_raw.json /data/raw/

Verify upload:

hdfs dfs -ls /data/raw

Expected output:

/data/raw/youtube_raw.json

Exit:

exit

5. Verify HDFS

Check file exists:

docker exec -it namenode hdfs dfs -ls /data/raw

Expected:

Found 1 items
/data/raw/youtube_raw.json

Check DataNode status:

docker exec -it namenode hdfs dfsadmin -report

Expected:

Live datanodes (1)

6. Run Spark ETL ( Option A)
i) Open the spark Container
docker exec -it spark-master bash

ii) Open PySpark
/opt/spark/bin/pyspark


iii) Run Spark job:
Copy thr PySpark Script

The ETL script will:

Read JSON from HDFS
Parse YouTube videos
Flatten comments
Create:
videos table
comments table
Load both tables into PostgreSQL

6. Run Spark ETL ( Option B)

Copy ETL script into Spark container if needed:

docker cp scripts/etl_spark.py spark-master:/opt/spark/

Run Spark job:

docker exec -it spark-master spark-submit /opt/spark/etl_spark.py

The ETL script will:

Read JSON from HDFS
Parse YouTube videos
Flatten comments
Create:
videos table
comments table
Load both tables into PostgreSQL

7. Verify Data in PostgreSQL

Open PostgreSQL:

docker exec -it postgres psql -U postgres -d youtube_db

List tables:

\dt

Expected:

videos
comments

Count records:

SELECT COUNT(*) FROM videos;

SELECT COUNT(*) FROM comments;

Example output:

videos   = 50
comments = 1231

Preview data:

SELECT * FROM videos LIMIT 5;

SELECT * FROM comments LIMIT 5;

Exit PostgreSQL:

\q
Useful Commands
Check running containers
docker ps
Stop environment
docker compose down
Restart environment
docker compose up -d
View NameNode UI

Open:

http://localhost:9870

View ResourceManager UI

Open:

http://localhost:8088

View Spark Master UI

Open:

http://localhost:8085

Connect to PostgreSQL
docker exec -it postgres psql -U postgres -d youtube_db
Final Pipeline
Run YouTube API extraction script
Upload JSON to HDFS
Verify HDFS storage
Run Spark ETL job
Load transformed data into PostgreSQL
Query PostgreSQL tables

Pipeline Flow:

YouTube API
↓
youtube_raw.json
↓
HDFS (/data/raw)
↓
Spark ETL
↓
videos + comments
↓
PostgreSQL
