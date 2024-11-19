from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    window,
    count,
    col,
    from_json,
    to_timestamp,
    current_timestamp,
)
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import sys
import os
from datetime import datetime
from pyspark.sql.functions import (
    window,
    count,
    col,
    from_json,
    to_timestamp,
    current_timestamp,
    coalesce,
)
from pyspark.sql import functions as F

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.kafka_setup import ensure_topics_exist
# emoji_cumulative_counts = {
# }

# Include Kafka connector package
packages = [
    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1",
    "org.apache.kafka:kafka-clients:3.4.1",
]
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import json

# Define the schema for the cumulative counts
cumulative_schema = StructType(
    [
        StructField("emoji_type", StringType(), True),
        StructField("emoji_count", IntegerType(), True),
        StructField("emoji_aggregated_count", IntegerType(), True),
    ]
)
spark = (
    SparkSession.builder.appName("EmojiStream")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1")
    .config("spark.jars.packages", ",".join(packages))
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.streaming.kafka.maxRatePerPartition", "1000")
    .config("spark.default.parallelism", "4")
    .config("spark.streaming.backpressure.enabled", "true")
    .config("spark.streaming.kafka.consumer.cache.enabled", "false")
    .config(
        "spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:log4j.properties"
    )
    .getOrCreate()
)

# spark = SparkSession.builder \
#     .appName("KafkaIntegrationWithAggregation") \
#     .master("local[*]") \
#     .config("spark.sql.streaming.schemaInference", "true") \
#     .getOrCreate()
#
spark.sparkContext.setLogLevel("WARN")
emoji_cumulative_counts_df = None


# Create a DataFrame for cumulative counts
# def create_cumulative_df(spark):
#    if not emoji_cumulative_counts['emoji_type']:  # If no cumulative data
#         # Return an empty DataFrame with the correct schema
#         return spark.createDataFrame([], ['emoji_type', 'emoji_count'])
#    else:
#     return spark.createDataFrame([(emoji, count) for emoji, count in zip(emoji_cumulative_counts['emoji_type'], emoji_cumulative_counts['emoji_count'])],['emoji_type', 'emoji_count'])
# Initialize the cumulative DataFrame or update it
def create_or_update_cumulative_df(new_counts_df):
    global emoji_cumulative_counts_df

    if emoji_cumulative_counts_df is None:
        # If it's the first batch, initialize with new_counts_df
        emoji_cumulative_counts_df = new_counts_df
    else:
        # Otherwise, update the cumulative counts by joining and summing
        emoji_cumulative_counts_df = emoji_cumulative_counts_df.join(
            new_counts_df, on="emoji_type", how="outer"
        ).select(
            "emoji_type",
            (
                coalesce(emoji_cumulative_counts_df["emoji_count"], F.lit(0))
                + coalesce(new_counts_df["emoji_count"], F.lit(0))
            ).alias("emoji_count"),
            (
                coalesce(emoji_cumulative_counts_df["emoji_aggregated_count"], F.lit(0))
                + coalesce(new_counts_df["emoji_aggregated_count"], F.lit(0))
            ).alias("emoji_aggregated_count"),
        )
    return emoji_cumulative_counts_df


def process_batch(df, epoch_id):
    try:
        # cumulative_df = create_cumulative_df(spark)
        if df.isEmpty():
            print(f"\nBatch {epoch_id}: No data to process")
            return

        # Process the data
        processed = df.groupBy("emoji_type").agg(count("*").alias("emoji_count"))
        # Update cumulative counts
        # for row in processed.collect():
        #     emoji_type = row['emoji_type']
        #     emoji_count = row['emoji_count']
        #     # Update the cumulative count for this emoji
        #     if emoji_type in emoji_cumulative_counts:
        #         emoji_cumulative_counts[emoji_type] += emoji_count
        #     else:
        #         emoji_cumulative_counts[emoji_type] = emoji_count
        # Log the current cumulative counts
        # print(f"Emoji cumulative counts so far: {emoji_cumulative_counts}")

        # Apply scaling
        scaled = processed.withColumn(
            "emoji_aggregated_count", (col("emoji_count") / 1000).cast("int") + 1
        )

        emoji_cumulative_counts_df = create_or_update_cumulative_df(scaled)
        # Add timestamp for the current batch
        # result = scaled.withColumn("processing_time", current_timestamp())
        # if emoji_cumulative_counts:
        #     # Write the cumulative counts to Kafka
        #     spark \
        #         .createDataFrame([(emoji_cumulative_,)], ["value"]) \
        #         .write \
        #         .format("kafka") \
        #         .option("kafka.bootstrap.servers", "localhost:9092") \
        #         .option("topic", "processed_emojis") \
        #         .save()
        # cumulative_data = json.dumps(emoji_cumulative_counts_df.collect())
        cumulative_data = json.dumps(emoji_cumulative_counts_df.collect())
        if cumulative_data:
            # Write the cumulative counts to Kafka
            spark.createDataFrame([(cumulative_data,)], ["value"]).write.format(
                "kafka"
            ).option("kafka.bootstrap.servers", "localhost:9092").option(
                "topic", "processed_emojis"
            ).save()
        # Write to Kafka if we have data
        # if result.count() > 0:
        #     result.selectExpr(
        #         "to_json(struct(emoji_type, emoji_count, scaled_count, processing_time)) AS value"
        #     ).write \
        #         .format("kafka") \
        #         .option("kafka.bootstrap.servers", "localhost:9092") \
        #         .option("topic", "processed_emojis") \
        #         .save()

        # Show results
        print(f"\nBatch {epoch_id} processed at {datetime.now()}")
        print(f"Records processed: {df.count()}")
    # result.show(truncate=False)

    except Exception as e:
        print(f"Error processing batch {epoch_id}: {str(e)}")


def main():
    if not ensure_topics_exist():
        print("Failed to create Kafka topics. Exiting...")
        sys.exit(1)

    print("Starting Spark streaming consumer...")

    # spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    # Schema for the incoming data
    schema = StructType(
        [
            StructField("user_id", StringType(), True),
            StructField("emoji_type", StringType(), True),
            StructField("timestamp", StringType(), True),
        ]
    )

    # Read from Kafka
    stream_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "emoji_stream")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .option("maxOffsetsPerTrigger", "1000")
        .load()
    )

    # Parse the JSON data
    parsed_df = (
        stream_df.selectExpr("CAST(value AS STRING) as json")
        .select(from_json(col("json"), schema).alias("data"))
        .select("data.*")
    )

    # Start the streaming query
    query = (
        parsed_df.writeStream.foreachBatch(process_batch)
        .trigger(processingTime="2 seconds")
        .start()
    )

    print("Stream processing started. Waiting for data...")
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nShutting down stream processing...")
        query.stop()
        spark.stop()


if __name__ == "__main__":
    main()
