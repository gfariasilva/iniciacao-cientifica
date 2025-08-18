import json
import boto3
import base64
import os


kinesis = boto3.client("kinesis")
STREAM_NAME = os.environ["KINESIS_STREAM"]


def lambda_handler(event, context):
    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event
        
        data = body.get("Data", "no-data")
        partition_key = body.get("PartitionKey", "default")

        # Envia para o Kinesis
        response = kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(data),
            PartitionKey=partition_key
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Record sent", "response": response})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
