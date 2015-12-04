'''
    ASMO's Attention Mechanism
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.interface

class Attention:
    def __init__(self, host):
        self.host = host
        
    def get_processes(self, is_async=False):
        return asmo.interface.get(self.host + '/process', is_async)
        
    def compete(self, is_async=False):
        return asmo.interface.post(self.host + '/compete', {}, is_async)
