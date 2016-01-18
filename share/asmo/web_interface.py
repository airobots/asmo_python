#!/usr/bin/env python

'''
    ASMO Web Interface
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import requests_futures.sessions
import json

session = requests_futures.sessions.FuturesSession()

def get(uri, is_async=False):
    task = session.get(uri)
    if is_async:
        response = task
    else:
        response = task.result().json()
    return response
    
def post(uri, content, is_async=False):
    task = session.post(uri, data=json.dumps(content), headers={'content-type': 'application/json'})
    if is_async:
        response = task
    else:
        response = task.result().json()
    return response
