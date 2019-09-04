#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Process
------------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

from . import configuration, web_interface, memory

_reflexes = {}
_non_reflexes = {}

class BaseProcess:
    def __init__(self, process_name):
        self.host = host
        self.process_name = process_name
        self.required_resources = []
        self.actions = []
        
    async def on_selected(self):
        pass
        
    async def run(self, *args, **kwargs):
        pass
        
        
class LocalReflexProcess(BaseProcess):
    def __init__(self, process_name):
        super().__init__(process_name)
        self.priority_level = 0.0
        self.memory = memory.LocalMemory()
        self.get_memory = self.memory.get
        self.set_memory = self.memory.set
        
    def propose(self, priority_level=None):
        if priority_level: self.priority_level = priority_level
        _reflexes[self.process_name] = {
            configuration.priority_level_key: self.attention_value,
            configuration.required_resources_key: self.required_resources,
            configuration.actions_key: self.actions
        }
        
        
class WebReflexProcess(BaseProcess):
    def __init__(self, process_name, host):
        super().__init__(process_name)
        self.priority_level = 0.0
        self.memory = memory.WebMemory(host)
        self.get_memory = self.memory.get
        self.set_memory = self.memory.set
        
    def propose(self, priority_level=None):
        if priority_level: self.priority_level = priority_level
        uri = '{0}/{1}/{2}'.format(self.host, configuration.process_uri, self.process_name)
        return web_interface.post(uri, {
            configuration.priority_level_key: self.attention_value,
            configuration.required_resources_key: self.required_resources,
            configuration.actions_key: self.actions
        })
        
        
class GeneralNonReflexProcess(BaseProcess):
    def __init__(self, process_name):
        super().__init__(process_name)
        self.accumulation_rate = 1.0
        self.objective_rate = 1.0
        self.subjective_rate = 1.0
        self.objective_weight = 0.0
        self.subjective_weight = 0.0
        self.attention_value = 0.0
        self.boost_value = 0.0
        self._total_attention_level = 0.0
        
    def update_total_attention_level(self):
        self._total_attention_level = self.attention_value + self.boost_value
        
    def update_attention_value(self):
        self.attention_value = self.accumulation_rate * self.attention_value + self.objective_rate * self.objective_weight + self.subjective_rate * self.subjective_weight
        
    def update_attention_and_propose(self, attention_value=None, required_resources=None, actions=None):
        if attention_value: self.attention_value = attention_value
        if required_resources: self.required_resources = required_resources
        if actions: self.actions = actions
        self.propose()
        
    def update_weights_and_propose(self, objective_weight=None, subjective_weight=None, required_resources=None, actions=None):
        if objective_weight: self.objective_weight = objective_weight
        if subjective_weight: self.subjective_weight = subjective_weight
        if required_resources: self.required_resources = required_resources
        if actions: self.actions = actions
        self.update_attention_value()
        self.propose()
        
    def propose(self):
        pass
        
        
class LocalNonReflexProcess(GeneralNonReflexProcess):
    def __init__(self, process_name):
        super().__init__(process_name)
        self.memory = memory.LocalMemory()
        self.get_memory = self.memory.get
        self.set_memory = self.memory.set
        
    def propose(self):
        self.update_total_attention_level()
        _non_reflexes[self.process_name] = {
            configuration.attention_value_key: self.attention_value,
            configuration.boost_value_key: self.boost_value,
            configuration.total_attention_level_key: self._total_attention_level,
            configuration.required_resources_key: self.required_resources,
            configuration.actions_key: self.actions
        }
        
        
class WebNonReflexProcess(GeneralNonReflexProcess):
    def __init__(self, process_name, host):
        super().__init__(process_name)
        self.memory = memory.WebMemory(host)
        self.get_memory = self.memory.get
        self.set_memory = self.memory.set
        
    def propose(self):
        uri = '{0}/{1}/{2}'.format(self.host, configuration.process_uri, self.process_name)
        return web_interface.post(uri, {
            configuration.attention_value_key: self.attention_value,
            configuration.boost_value_key: self.boost_value,
            configuration.required_resources_key: self.required_resources,
            configuration.actions_key: self.actions
        })
        
        
ReflexProcess = WebReflexProcess
NonReflexProcess = WebNonReflexProcess