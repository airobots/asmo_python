#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Attention Mechanism
------------------------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

import argparse, time, json, subprocess, shlex
from . import configuration, web_interface, process as asmo_process

_winners = {}
_start_time = 0
_history = {}

class LocalAttention:
    def __init__(self):
        self.host = None
        _start_time = time.time()
        
    def get_reflex_processes(self, is_async=False):
        return asmo_process._reflexes
        
    def get_non_reflex_processes(self, is_async=False):
        return asmo_process._non_reflexes
        
    def get_all_processes(self, is_async=False):
        processes = {}
        processes.update(asmo_process._non_reflexes)
        processes.update(asmo_process._reflexes)
        return processes
        
    def compete(self, is_async=False):
        duration = time.time() - _start_time
        ranked_processes = rank_attention(asmo_process._reflexes, asmo_process._non_reflexes)
        (_winners, actions, used_resources) = choose_winners(ranked_processes, [])
        asmo_process._reflexes = {}
        asmo_process._non_reflexes = {}
        series = {}
        # history does not need values from ranked_processes
        #   instead, it will also work with values from asmo_process._reflexes and asmo_process._non_reflexes
        #   however, processes used to determine the winners should be the same with processes used to record in history
        for (name, details) in ranked_processes:
            _history.setdefault(name, [])
            _history[name].append({'x': duration, 'y': details[configuration.total_attention_level_key]})
            series[name] = _history[name]
        return {'winners': _winners, 'actions': actions, 'used_resources': used_resources}
        
        
class WebAttention:
    def __init__(self, host):
        self.host = host
        
    def get_all_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, configuration.process_uri)
        return web_interface.get(uri, is_async)
        
    def get_reflex_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, configuration.process_uri)
        return web_interface.get(uri, is_async)
        
    def get_non_reflex_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, configuration.process_uri)
        return web_interface.get(uri, is_async)
        
    def compete(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, configuration.compete_uri)
        return web_interface.post(uri, {}, is_async)
        
        
def set_total_attention_level(dict_item):
    values = dict_item[1]
    values[configuration.total_attention_level_key] = values[configuration.attention_value_key] + values[configuration.boost_value_key]
    return values[configuration.total_attention_level_key]
    
def rank_attention(reflex_processes, non_reflex_processes):
    sorted_reflex = sorted(reflex_processes.items(), key=lambda x: x[1][configuration.priority_level_key], reverse=True)
    sorted_non_reflex = sorted(non_reflex_processes.items(), key=set_total_attention_level, reverse=True)
    return sorted_reflex + sorted_non_reflex
    
def choose_winners(ranked_processes, used_resources):
    winners = {}
    actions = {}
    for (name, details) in ranked_processes:
        # Check if required resources are available
        is_available = True
        for resource in details[configuration.required_resources_key]:
            if resource in used_resources:
                is_available = False
                break
        # Choose as a winner if required resources are available
        if is_available:
            used_resources.extend(details[configuration.required_resources_key])
            winners[name] = details
            actions.update(details[configuration.actions_key])
    return (winners, actions, used_resources)