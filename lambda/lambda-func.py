import json
import boto3

s3 = boto3.client("s3")

def lambda_handler(event,context):
    bucket_name = "BUCKET_NAME"
    object_key = "hello-world.txt"

    s3.put_object(
        Bucket = bucket_name,
        Key = object_key,
        Body = "Hello world!!!!"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(f"File uploaded to {bucket_name}/{object_key}")
    }

