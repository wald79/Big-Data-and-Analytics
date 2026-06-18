from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
import json

# -----------------------------
# 1. Spark Session
# -----------------------------
spark = SparkSession.builder \
    .appName("YouTube ETL Pipeline") \
    .getOrCreate()

# -----------------------------
# 2. Read raw JSON from HDFS
# -----------------------------
raw = spark.read.text("hdfs://namenode:8020/data/raw/youtube_raw.json")

json_string = "\n".join(row.value for row in raw.collect())
data = json.loads(json_string)

df = spark.createDataFrame(data)

# -----------------------------
# 3. Transform: Videos table
# -----------------------------
videos_df = df.select(
    col("video.video_id").alias("video_id"),
    col("video.title").alias("title"),
    col("video.channel_title").alias("channel_title"),
    col("video.description").alias("description"),
    col("video.published_at").alias("published_at")
)

# -----------------------------
# 4. Transform: Comments table
# -----------------------------
flat_comments = df.select(
    col("video.video_id").alias("video_id"),
    explode("comments").alias("comment")
).select(
    "video_id",
    col("comment.author").alias("author"),
    col("comment.text").alias("text"),
    col("comment.likes").alias("likes"),
    col("comment.published_at").alias("published_at")
)

# -----------------------------
# 5. PostgreSQL config
# -----------------------------
jdbc_url = "jdbc:postgresql://postgres:5432/youtube_db"

db_properties = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

# -----------------------------
# 6. Write to PostgreSQL
# -----------------------------

# Videos table
videos_df.write \
    .mode("overwrite") \
    .jdbc(url=jdbc_url, table="videos", properties=db_properties)

# Comments table
flat_comments.write \
    .mode("overwrite") \
    .jdbc(url=jdbc_url, table="comments", properties=db_properties)

# -----------------------------
# 7. Stop Spark
# -----------------------------
spark.stop()