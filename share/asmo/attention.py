#!/usr/bin/env python

'''
    ASMO's Attention Mechanism
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import time
import json
import subprocess
import shlex
import asmo.configuration
import asmo.interface

class Attention:
    def __init__(self, host):
        self.host = host
        
    def get_processes(self, is_async=False):
        url = '{0}/{1}'.format(self.host, asmo.configuration.process_uri)
        return asmo.interface.get(url, is_async)
        
    def compete(self, is_async=False):
        url = '{0}/{1}'.format(self.host, asmo.configuration.compete_uri)
        return asmo.interface.post(url, {}, is_async)
        
def run(attention):
    results = attention.compete()
    for (action, parameters) in results.get(asmo.configuration.actions_key, {}).items():
        arguments = shlex.split(action)
        arguments.append(json.dumps(parameters))
        p = subprocess.Popen(arguments)
    return True
    
def main():
    attention = Attention(asmo.configuration.host)
    print("[ OK ] Start ASMO's Attention Mechanism")
    while run(attention):
        time.sleep(asmo.configuration.competition_time)
        
if __name__ == '__main__':
    main()
