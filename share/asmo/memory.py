'''
    ASMO's Memory
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.interface

class Memory:
    def __init__(self, host):
        self.host = host
        
    def read_data(self, location, is_async=False):
        return asmo.interface.get(self.host + '/memory/' + location, is_async)
        
    def write_data(self, location, content, is_async=False):
        return asmo.interface.post(self.host + '/memory/' + location, content, is_async)
