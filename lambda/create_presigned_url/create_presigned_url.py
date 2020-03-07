#!/usr/bin/env python3

####################
# IMPORTS
####################
import os
import json
import boto3
from botocore.exceptions import ClientError
import secrets
import urllib.parse

####################
# Environment Vars:
# UPLOAD_BUCKET_NAME
####################

####################
# METHODS
####################
def handler(event, context):
    uploadBucket = os.environ['UPLOAD_BUCKET_NAME']
    filename = None
    if "queryStringParameters" in event:
        if "filename" in event["queryStringParameters"]:
            filename = event["queryStringParameters"]["filename"]
            print("Upload file: {}".format(filename))
    if filename is None:
        return generateResponse('400', "Missing File name")
    filename = urllib.parse.unquote(filename)
    key_path = secrets.token_hex(16) + '/' + filename

    try:
        s3_client = boto3.client('s3')
        presigned_url = s3_client.generate_presigned_post(uploadBucket, key_path, Conditions=[{'acl': "private"}])
    except ClientError as err:
        print("ERROR: S3 Error %s" % err)
        return generateResponse('400', "S3 Client Error")
    return generateResponse('200', presigned_url)

def generateResponse(status, message):
    return {
        "statusCode": str(status),
        "headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(message)
    }