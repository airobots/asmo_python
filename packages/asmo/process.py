#!/usr/bin/env python

'''
    ASMO Process
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo.configuration
import asmo.web_interface
import asmo.memory

_reflexes = {}
_non_reflexes = {}

class ReflexProcess(asmo.memory.Memory):
    def __init__(self, host, process_name, run_function):
        self.host = host
        self.process_name = process_name
        self.priority_level = 0.0
        self.required_resources = []
        self.actions = []
        self.run = run_function
        
    def _local_propose(self, priority_level=None):
        if priority_level: self.priority_level = priority_level
        _reflexes[self.process_name] = \
        {
            asmo.configuration.priority_level_key: self.attention_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        return {'ok': True}
        
    def _web_propose(self, priority_level=None):
        if priority_level: self.priority_level = priority_level
        content = \
        {
            asmo.configuration.priority_level_key: self.attention_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        uri = '{0}/{1}/{2}'.format(self.host, asmo.configuration.process_uri, self.process_name)
        return asmo.web_interface.post(uri, content)
        
    propose = _web_propose
    
    
class NonReflexProcess(asmo.memory.Memory):
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
        self._total_attention_level = 0.0
        self.required_resources = []
        self.actions = []
        self.run = run_function
        
    def _update_total_attention_level(self):
        self._total_attention_level = self.attention_value + self.boost_value
        
    def _local_propose(self, attention_value=None):
        if attention_value: self.attention_value = attention_value
        self._update_total_attention_level()
        _non_reflexes[self.process_name] = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.total_attention_level_key: self._total_attention_level,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        return {'ok': True}
        
    def _local_propose_with_weights(self, objective_weight=None, subjective_weight=None):
        if objective_weight: self.objective_weight = objective_weight
        if subjective_weight: self.subjective_weight = subjective_weight
        self.update_attention_value()
        self._update_total_attention_level()
        _non_reflexes[self.process_name] = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.total_attention_level_key: self._total_attention_level,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        return {'ok': True}
        
    def _web_propose(self, attention_value=None):
        if attention_value: self.attention_value = attention_value
        content = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        uri = '{0}/{1}/{2}'.format(self.host, asmo.configuration.process_uri, self.process_name)
        return asmo.web_interface.post(uri, content)
        
    def _web_propose_with_weights(self, objective_weight=None, subjective_weight=None):
        if objective_weight: self.objective_weight = objective_weight
        if subjective_weight: self.subjective_weight = subjective_weight
        self.update_attention_value()
        content = \
        {
            asmo.configuration.attention_value_key: self.attention_value,
            asmo.configuration.boost_value_key: self.boost_value,
            asmo.configuration.required_resources_key: self.required_resources,
            asmo.configuration.actions_key: self.actions
        }
        uri = '{0}/{1}/{2}'.format(self.host, asmo.configuration.process_uri, self.process_name)
        return asmo.web_interface.post(uri, content)
        
    def update_attention_value(self):
        self.attention_value = self.accumulation_rate * self.attention_value + self.objective_rate * self.objective_weight + self.subjective_rate * self.subjective_weight
        
    propose = _web_propose
    propose_with_weights = _web_propose_with_weights
