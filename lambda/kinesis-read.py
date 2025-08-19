import base64
import json
import os
import uuid

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMO_TABLE"])


def lambda_handler(event, context):
    try:
        if "Records" in event:
            records = event["Records"]
        elif "body" in event:
            body = json.loads(event["body"])
            records = body.get("Records", [])
        else:
            records = []

        for record in records:
            payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
            print("Recebido do Kinesis:", payload)

            data = json.loads(payload)

            data["trip_id"] = str(uuid.uuid4())

            table.put_item(Item=data)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Dados salvos no DynamoDB"}),
        }

    except Exception as e:
        print("Erro:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
