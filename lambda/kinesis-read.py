import base64


def lambda_handler(event, context):
    try:
        if "body" in event:
            body = json.loads(event["body"])
        else:
            body = event

        for record in body.get("Records"):
            payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
            print("Recebido do Kinesis:", payload)

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
