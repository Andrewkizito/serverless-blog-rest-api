import os
import json
import boto3
from decimal import Decimal


def decimalParser(obj):
    if isinstance(obj, Decimal):
        return float(obj)

    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable")


def handler(event, context):
    pathParamters = event['pathParameters']
    dynamodb = boto3.resource("dynamodb")
    db = dynamodb.Table(os.environ.get("TABLE_NAME"))

    # Setting up orm
    dynamodb = boto3.resource("dynamodb")
    db = dynamodb.Table(os.environ.get("TABLE_NAME"))

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
    }

    if pathParamters['id']:
        try:
            response = db.get_item(
                Key={
                    "PK": "BLOG",
                    "SK": "ARTICLE#{}".format(pathParamters['id'])}
            )

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps(response['Item'], default=decimalParser),
            }

        except Exception as e:
            print(e)
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps("Something went wrong"),
            }

    return {
        "statusCode": 400,
        "headers": headers,
        "body": json.dumps("Id not defined"),
    }
