# Project 3 — Real-Time NYC Taxi Streaming Pipeline

## What this project does
Streams NYC Yellow Taxi trip data in real time using AWS Kinesis.
A Python producer sends taxi trip records into Kinesis Data Streams.
Kinesis Firehose automatically collects, converts to Parquet, and delivers to S3.
Glue Catalog registers the schema. Athena queries the data with SQL.

## Architecture
```
Python Producer → Kinesis Data Stream → Kinesis Firehose → S3 (Parquet) → Glue Catalog → Athena
```

## Services used
| Service | Role |
|---|---|
| AWS CloudShell | Runs the Python producer script |
| Kinesis Data Streams | Receives records in real time, 2 shards |
| Kinesis Firehose | Buffers 60s, converts to Parquet, delivers to S3 |
| Amazon S3 | Stores Parquet files partitioned by year/month/day/hour |
| AWS Glue Catalog | Holds schema for nyc_streaming_trips table |
| Amazon Athena | SQL queries directly on S3 Parquet files |

## Key concepts demonstrated
- Streaming vs batch pipeline design
- Partition key selection for balanced shard distribution
- Firehose format conversion using Glue schema
- Dynamic S3 partitioning by timestamp
- Decoupled producer-consumer architecture

## Dataset
NYC Yellow Taxi Trip Records — January 2024
Source: NYC Taxi and Limousine Commission (TLC)
File: yellow_tripdata_2024-01.parquet (2.9M rows, 47.6 MB)

## S3 structure
```
nyc-trips-pipeline-ravindra/
└── streaming/
    └── year=2026/
        └── month=03/
            └── day=31/
                └── hour=09/
                    └── nyc-trips-delivery-1-*.gz.parquet
```

## Sample Athena query
```sql
SELECT 
    pulocationid,
    COUNT(*) as trip_count,
    ROUND(AVG(fare_amount), 2) as avg_fare,
    ROUND(SUM(total_amount), 2) as total_revenue
FROM nyc_streaming_trips
GROUP BY pulocationid
ORDER BY trip_count DESC
LIMIT 10;
```

## Lessons learned
- Firehose delivers .gz files by default — Parquet conversion requires a Glue table schema
- Partition key must have high cardinality — used PULocationID (200+ unique zones)
- Same partition key always routes to same shard — guaranteed ordering per key
- Glue table must exist BEFORE enabling Firehose format conversion
```

