import os
import re
import json
import boto3
from datetime import datetime


def handler(event, context):
    print(context)
    # Initializing boto3
    s3 = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    db = dynamodb.Table(os.environ.get("TABLE_NAME"))

    # Parsing request body
    payload = json.loads(event["body"])

    # Initializing date
    date_today = datetime.today()
    timestamp = datetime.timestamp(date_today)
    if "timestamp" in payload:
        timestamp = payload["timestamp"]

    # Setting up path
    path = re.sub(" ", "-", payload["title"].lower())

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
    }

    # Writing to file
    with open(f"/tmp/{path}.html", "w+") as file:
        file.write(payload["content"])
        file.close()

    with open(f"/tmp/{path}.html", "rb") as data:
        try:
            s3.upload_fileobj(
                data, os.environ.get("BUCKET_NAME"), f"public/{path}.html"
            )
        except Exception as error:
            print(error)
            return {
                "statusCode": 400,
                "headers": headers,
                "body": "Something Went Wrong",
            }

    try:
        db.put_item(
            Item={
                "PK": "BLOG",
                "SK": f"ARTICLE#{path}",
                "title": payload["title"],
                "description": payload["description"],
                "image": payload["image"],
                "author": payload["author"],
                "content": f"public/{path}.html",
                "timestamp": int(timestamp),
                "date": date_today.strftime("%d-%B-%Y"),
            }
        )

        return {
            "statusCode": 200,
            'headers': headers,
            "body": "Article Published Successfully",
        }

    except Exception as error:
        print(error)
        return {
            "statusCode": 500,
            'headers': headers,
            "body": "Something Went Wrong",
        }
