#!/usr/bin/env python3

####################
# IMPORTS
####################
import os
import boto3
from botocore.exceptions import ClientError
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

####################
# Environment Vars:
# DATABASE_URL
# S3_TRANSCODED_BUCKET_URL : https://s3.amazonaws.com/YOUR_TRANSCODED_BUCKET_NAME_HERE
####################

####################
# METHODS
####################
def handler(event, context):
    # Need to handle file name with space ' ' where S3 url will encode with '+'
    source_key = event["Records"][0]["s3"]["object"]["key"]
    video_url = os.environ['S3_TRANSCODED_BUCKET_URL'] + '/' + source_key
    unique_key = source_key.split('/')[0]
    data = {
        'transcoding': False,
        'source': video_url
    }

    dir_path = os.path.dirname(os.path.realpath(__file__))
    cred = credentials.Certificate(dir_path + "/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, { 'databaseURL': os.environ['DATABASE_URL'] })
    root = db.reference()
    root.child('videos').child(unique_key).set(data)
    print("INFO: Added to Firebase: {}".format(video_url))
    return
