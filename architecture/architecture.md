# Architecture — Kinesis Streaming Pipeline

## Full data flow

### Step 1 — Producer (Python script on CloudShell)
- Reads nyc_taxi.csv row by row
- Calls boto3 put_record() for each row
- Partition key = PULocationID (200+ unique NYC pickup zones)
- Same PULocationID always routes to same shard
- Sends 100 records with 0.1s delay simulating real-time feed

### Step 2 — Kinesis Data Stream (nyc-trips-stream)
- 2 shards, Provisioned mode
- Each shard: 1 MB/s write, 2 MB/s read
- Records held for 24 hours (retention)
- Multiple consumers can read same records independently
- Ordered within each shard by sequence number

### Step 3 — Kinesis Firehose (nyc-trips-delivery)
- Source: nyc-trips-stream (polls continuously)
- Buffer: 60 seconds or 5 MB whichever comes first
- Format conversion: JSON → Parquet using Glue schema
- Destination: S3 with dynamic partitioning prefix
- Zero consumer code written

### Step 4 — S3 (nyc-trips-pipeline-ravindra)
- Prefix: streaming/year=!/month=!/day=!/hour=!/
- Firehose fills timestamp values automatically
- Files stored as Parquet with GZIP compression
- Partitioned layout enables Athena partition pruning

### Step 5 — Glue Data Catalog
- Database: nyc-trips-db
- Table: nyc_streaming_trips
- 19 columns manually defined matching CSV schema
- Location points to s3://nyc-trips-pipeline-ravindra/streaming/
- Used by both Firehose (format conversion) and Athena (querying)

### Step 6 — Athena
- Reads schema from Glue Catalog
- Scans Parquet files directly on S3
- Pay per TB scanned — Parquet reduces cost 10x vs JSON
- No database server, no data loading needed

## Key architectural decisions

### Why 2 shards not 1
Each shard handles 1 MB/s write. NYC taxi data bursts during peak hours.
2 shards = 2 MB/s capacity with headroom.

### Why PULocationID as partition key
High cardinality (200+ unique zones) ensures even distribution across shards.
Low cardinality keys like VendorID (only 2 values) would cause hot shards.

### Why Firehose over custom consumer
No consumer code needed. AWS manages buffering, retry, format conversion.
Firehose is the right tool when destination is S3/Redshift with no custom logic.

### Why Parquet over JSON
Columnar format — Athena reads only queried columns.
SELECT fare_amount reads 1 column not all 19.
Result: 10x less data scanned, 10x lower cost.

### Why same bucket as Projects 1 and 2
One S3 bucket = one data lake. Separated by prefix not by bucket.
This is the real-world production pattern.
