#!/usr/bin/env python

'''
    ASMO Process
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.configuration
import asmo.interface

class NonReflexProcess:
    def __init__(self, host, process_name, run_function):
        self.host = host
        self.process_name = process_name
        self.accumulation_rate = 1.0
        self.objective_rate = 1.0
        self.subjective_rate = 1.0
        self.objective_weight = 0.0
        self.subjective_weight = 0.0
        self.attention_value = 0.0
        self.boost_value = 0.0
        self.required_resources = []
        self.actions = []
        self.run = run_function
        
    def calculate_attention_value(self):
        self.attention_value = self.accumulation_rate * self.attention_value + self.objective_rate * self.objective_weight + self.subjective_rate * self.subjective_weight
        
    def propose(self, attention_value=None):
        if attention_value: self.attention_value = attention_value
        content = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.process_uri, self.process_name)
        return asmo.interface.post(url, content)
        
    def propose_with_weights(self, objective_weight=None, subjective_weight=None):
        if objective_weight: self.objective_weight = objective_weight
        if subjective_weight: self.subjective_weight = subjective_weight
        self.calculate_attention_value()
        content = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.process_uri, self.process_name)
        return asmo.interface.post(url, content)
        
    def read_data(self, location, is_async=False):
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.interface.get(url, is_async)
        
    def write_data(self, location, content):
        url = '{0}/{1}/{2}'.format(self.host, asmo.configuration.memory_uri, location)
        return asmo.interface.post(url, content)
