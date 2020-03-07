#!/usr/bin/env python3

####################
# IMPORTS
####################
import os
import json
from jose import jwt
import requests

####################
# Environment Vars:
# AUTH0_DOMAIN
####################

####################
# METHODS
####################
def handler(event, context):
    # The authorization token is in the form of "Authentication": "Bearer (some ID token from the frontent)"
    jwtToken = None
    if "authorizationToken" in event:
        jwtToken = event['authorizationToken'].split(' ')[1]
    if jwtToken is None:
        print("ERROR: Missing JWT Token")
        return
    
    auth0Domain = os.environ['AUTH0_DOMAIN']
    httpResponse = requests.get("https://{0}/.well-known/jwks.json".format(auth0Domain))
    if httpResponse.status_code != 200:
        print("ERROR: No jwt keys")
        return
    jwtsKey = httpResponse.json()["keys"][0]
    try:
        verifyJWTToken(jwtToken, jwtsKey)
    except Exception:
        print("ERROR: Authorization Failed")
        return

    return generatePolicy('user', 'allow', event["methodArn"])

def verifyJWTToken(jwtToken, jwksKey):
    if jwksKey["alg"] != 'RS256':
        raise ValueError('ERR: Only support RS256')
    if "kid" not in jwksKey :
        raise ValueError('ERR: Invalid signing algorithm')
    verify_opts = {
        "verify_aud": False,
        "verify_sub": False,
        "verify_exp": False,
        "verify_at_hash": False
    }
    jwt.decode(jwtToken, jwksKey, options=verify_opts)
    # return if there is no error/exception when decode with provided jwt key set
    return

def generatePolicy(principalId, effect, resource):
    policyResponse = {}
    policyResponse["principalId"] = principalId
    policyDocument = {
        "Version": '2012-10-17',
        "Statement": [{
            "Action": 'execute-api:Invoke',
            "Effect": effect,
            "Resource": resource
        }]
    }
    policyResponse["policyDocument"] = policyDocument
    return policyResponse