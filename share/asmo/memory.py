#!/usr/bin/env python

'''
    ASMO's Memory
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.configuration
import asmo.web_interface

_dict = {}

class Memory:
    def __init__(self, host):
        self.host = host
        
    def _local_read_data(self, location, is_async=False):
        return _dict.get(location)
        
    def _local_write_data(self, location, content, is_async=False):
        _dict[location] = content
        return {'ok': True}
        
    def _web_read_data(self, location, is_async=False):
        uri = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.web_interface.get(uri, is_async)
        
    def _web_write_data(self, location, content, is_async=False):
        uri = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.web_interface.post(uri, content, is_async)
        
    read_data = _web_read_data
    write_data = _web_write_data
