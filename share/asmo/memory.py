#!/usr/bin/env python

'''
    ASMO's Memory
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.configuration
import asmo.interface

class Memory:
    def __init__(self, host):
        self.host = host
        
    def read_data(self, location, is_async=False):
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.interface.get(url, is_async)
        
    def write_data(self, location, content, is_async=False):
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.interface.post(url, content, is_async)
