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
# ELASTIC_TRANSCODER_REGION
# ELASTIC_TRANSCODER_PIPELINE_ID
# DATABASE_URL
####################

####################
# METHODS
####################
def handler(event, context):
    pipelineID = os.environ['ELASTIC_TRANSCODER_PIPELINE_ID']
    # Need to handle file name with space ' ' where S3 url will encode with '+'
    source_key = event["Records"][0]["s3"]["object"]["key"]
    print("INFO: Source key:",source_key)
    output_key = source_key.split('.')[0]
    print("INFO: Output key:", output_key)
    unique_key = output_key.split('/')[0]

    try:
        transcoder_client = boto3.client('elastictranscoder', os.environ['ELASTIC_TRANSCODER_REGION'])
        outputs_params = [{
            'Key': output_key + '-web-480p.mp4',
            'PresetId': '1351620000001-000020'
        }]
        transcoder_client.create_job(PipelineId=pipelineID, OutputKeyPrefix=output_key+'/', Input={'Key':source_key}, Outputs=outputs_params)
    except ClientError as err:
        print("ERROR: Transcoder Error %s" % err)
        return
    addVideoEntryToDb(unique_key)
    return


def addVideoEntryToDb(key):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cred = credentials.Certificate(dir_path + "/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, { 'databaseURL': os.environ['DATABASE_URL'] })
    root = db.reference()
    return root.child('videos').child(key).set({ 'transcoding': True })