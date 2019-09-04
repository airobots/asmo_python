#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Memory
-----------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

from . import configuration, web_interface

_dict = {}

class LocalMemory:
    def get(self, location, default=None):
        return _dict.get(location, default)
        
    def set(self, location, content):
        _dict[location] = content
        
        
class WebMemory:
    def __init__(self, host):
        self.host = host
        
    def get(self, location, is_async=False):
        uri = '{0}/{1}/{2}'.format(self.host, configuration.memory_uri, location)
        return web_interface.get(uri, is_async)
        
    def set(self, location, content, is_async=False):
        uri = '{0}/{1}/{2}'.format(self.host, configuration.memory_uri, location)
        return web_interface.post(uri, content, is_async)
        
        
Memory = WebMemory