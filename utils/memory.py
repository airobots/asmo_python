'''
    ASMO Memory Utility
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import requests
import json

host = 'http://localhost:8000'
json_headers = {'content-type': 'application/json'}

def write_data(uri, content):
    requests.put(host + '/memory/' + uri, data = json.dumps(content), headers = json_headers)
    
def read_data(uri):
    return requests.get(host + '/memory/' + uri).json()
