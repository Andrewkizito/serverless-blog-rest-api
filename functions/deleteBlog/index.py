import os
import json
import boto3
from datetime import datetime


def handler(event, context):
    # Initializing boto3
    s3 = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    db = dynamodb.Table(os.environ.get("TABLE_NAME"))

    # Parsing request body
    payload = json.loads(event["body"])

    objects_to_delete = []

    for item in payload["files"]:
        objects_to_delete.append({"Key": item})

    try:
        db.delete_item(
            Key={
                "PK": payload["PK"],
                "SK": payload["SK"],
            }
        )

        s3.delete_objects(
            Bucket=os.environ.get("BUCKET_NAME"),
            Delete={"Objects": objects_to_delete},
        )

        return {
            "statusCode": 200,
            "body": "Item Deleted Successfully",
            "headers": {
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
        }

    except Exception as error:
        print(error)
        return {
            "statusCode": 400,
            "body": "Something Went Wrong",
            "headers": {
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
            },
        }
