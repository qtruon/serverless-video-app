#!/usr/bin/env python3

####################
# IMPORTS
####################
import os
import json
import requests

####################
# Environment Vars:
# AUTH0_DOMAIN
####################

####################
# METHODS
####################

def handler(event, context):
    accessToken = None
    if "queryStringParameters" in event:
        if "accessToken" in event["queryStringParameters"]:
            accessToken = event["queryStringParameters"]["accessToken"]
            print("Access token: {0}".format(accessToken))
    if accessToken is None:
        return generateResponse('400', "Missing Access Token")
    
    auth0Domain = os.environ['AUTH0_DOMAIN']
    httpResponse = requests.post("https://{0}/userinfo".format(auth0Domain), headers={ 'Authorization': "Bearer {0}".format(accessToken) })

    return generateResponse(httpResponse.status_code, httpResponse.json())

def generateResponse(status, message):
    return {
        "statusCode": str(status),
        "headers": { 'Access-Control-Allow-Origin': '*' },
        "body": json.dumps(message)
    }