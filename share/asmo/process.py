'''
    ASMO Process
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

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
            "attention_value": self.attention_value,
            "boost_value": self.boost_value,
            "required_resources": self.required_resources,
            "actions": self.actions
        }
        return asmo.interface.post(self.host + '/process/' + self.process_name, content)
        
    def propose_with_weights(self, objective_weight=None, subjective_weight=None):
        if objective_weight: self.objective_weight = objective_weight
        if subjective_weight: self.subjective_weight = subjective_weight
        self.calculate_attention_value()
        content = \
        {
            "attention_value": self.attention_value,
            "boost_value": self.boost_value,
            "required_resources": self.required_resources,
            "actions": self.actions
        }
        return asmo.interface.post(self.host + '/process/' + self.process_name, content)
        
    def read_data(self, location, is_async=False):
        return asmo.interface.get(self.host + '/memory/' + location, is_async)
        
    def write_data(self, location, content):
        return asmo.interface.post(self.host + '/memory/' + location, content)
