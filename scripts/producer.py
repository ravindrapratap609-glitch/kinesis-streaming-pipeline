Type this in CloudShell to create the file:


cat > producer.py << 'EOF'
import boto3, csv, json, time, os

STREAM_NAME   = "nyc-trips-stream"
REGION        = "us-east-1"
CSV_FILE      = "/home/clouduser/nyc_taxi.csv"
RECORDS_LIMIT = 100
DELAY_SECONDS = 0.1

kinesis = boto3.client("kinesis", region_name=REGION)

def send_record(row, row_number):
    partition_key = row.get("trip_id") or row.get("VendorID") or str(row_number)
    response = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(row).encode("utf-8"),
        PartitionKey=str(partition_key)
    )
    print(f"[Row {row_number:>4}]  shard={response['ShardId']}  http={response['ResponseMetadata']['HTTPStatusCode']}")

def main():
    print(f"Sending to stream: {STREAM_NAME}\n")
    sent = 0
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            if RECORDS_LIMIT and i > RECORDS_LIMIT:
                break
            try:
                send_record(row, i)
                sent += 1
            except Exception as e:
                print(f"[Row {i}] FAILED — {e}")
            time.sleep(DELAY_SECONDS)
    print(f"\nDone. Sent {sent} records.")
    print("Wait 60s then check S3 streaming/ prefix for Parquet file.")

if __name__ == "__main__":
    main()
EOF
