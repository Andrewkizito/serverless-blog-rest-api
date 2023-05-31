import os
import json
import boto3
import urllib.request
from hashlib import md5
from datetime import date

headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
}


def generate_expression(data):
    expression = "set "
    # Main Content
    if "title" in data:
        expression = expression + "title = :tit,"
    if "description" in data:
        expression = expression + "description = :des,"
    if "content" in data:
        expression = expression + "content = :cont,"
    if "image" in data:
        expression = expression + "image = :img,"
    if "author" in data:
        expression = expression + "author = :aut,"
    expression = expression + "last_update = :lu"

    return expression


def generate_values(data):
    values = {}
    # Main Content
    if "title" in data:
        values[":tit"] = data["title"]
    if "description" in data:
        values[":des"] = data["description"]
    if "image" in data:
        values[":img"] = data["image"]
    if "content" in data:
        values[":cont"] = data["content"]
    if "author" in data:
        values[":aut"] = data["author"]

    date_today = date.today()
    values[":lu"] = f"{date_today}"

    return values


def handler(event, context):
    # Intializing apis
    dynamodb = boto3.resource("dynamodb")
    db = dynamodb.Table(os.environ.get("TABLE_NAME"))

    # Parsing payload
    paramters = event['pathParameters']
    payload = json.loads(event["body"])

    # Getting post id
    id = paramters['id']
    # Getting s3 bucket name
    bucketName = os.environ.get('BUCKET_NAME')

    # Checking if content is in payload
    if 'content' in payload:
        url = f'https://{bucketName}.s3.eu-central-1.amazonaws.com/public/{id}.html'
        res = urllib.request.urlopen(url)

        if res.getcode() != 200:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": "Failed to download original content",
            }

        # Generating hashes for the content in payload and current blog content
        currentHash = md5(res.read()).hexdigest()
        newHash = md5(payload['content'].encode('utf-8')).hexdigest()

        # Checking if data has changes by comparing hashes
        if currentHash != newHash:
            s3 = boto3.client('s3')
            # Writing to file
            with open(f"/tmp/{id}.html", "w+") as file:
                file.write(payload["content"])
                file.close()

            with open(f"/tmp/{id}.html", "rb") as data:
                try:
                    s3.upload_fileobj(
                        data, bucketName, f"public/{id}.html"
                    )
                    payload['content'] = f"public/{id}.html"

                except Exception as error:
                    print(error)
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Access-Control-Allow-Headers": "*",
                            "Access-Control-Allow-Origin": "*",
                        },
                        "body": "Something Went Wrong",
                    }

        else:
            del payload['content']

    expression = generate_expression(payload)
    values = generate_values(payload)

    try:
        db.update_item(
            Key={
                "PK": payload["PK"],
                "SK": payload["SK"],
            },
            UpdateExpression=expression,
            ExpressionAttributeValues=values,
        )
        return {
            "statusCode": 200,
            "headers": headers,
            "body": "Updates Applied Successfully",
        }

    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "headers": headers,
            "body": "Something Went Wrong",
        }
