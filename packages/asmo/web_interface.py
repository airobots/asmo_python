#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Web Interface
------------------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

import json
import requests_futures.sessions

class WebInterface:
    def __init__(self, session=None):
        self.session = session or requests_futures.sessions.FuturesSession()
        
    def async_get(self, uri):
        return self.session.get(uri)
        
    def sync_get(self, uri):
        return self.async_get(uri).result()
        
    def sync_get_json(self, uri):
        return self.sync_get(uri).json()
        
    def async_post(self, uri, data, headers={}):
        return self.session.post(uri, data=data, headers=headers)
        
    def async_post_json(self, uri, content):
        return self.async_post(uri, json.dumps(content), headers={'content-type': 'application/json'})
        
    def sync_post(self, uri, content):
        return self.async_post(uri).result()
        
    def sync_post_json(self, uri, content):
        return self.async_post_json(uri).json()
        
    get = async_get
    post = async_post
    
    
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