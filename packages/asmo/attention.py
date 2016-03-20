#!/usr/bin/env python

'''
    ASMO's Attention Mechanism
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import time
import json
import subprocess
import shlex
import argparse
import asmo.configuration
import asmo.web_interface
import asmo.process

_winners = {}
_start_time = 0
_history = {}

class LocalAttention:
    def __init__(self, host):
        self.host = host
        _start_time = time.time()
        
    def get_reflex_processes(self, is_async=False):
        return asmo.process._reflexes
        
    def get_non_reflex_processes(self, is_async=False):
        return asmo.process._non_reflexes
        
    def get_all_processes(self, is_async=False):
        processes = {}
        processes.update(asmo.process._non_reflexes)
        processes.update(asmo.process._reflexes)
        return processes
        
    def compete(self, is_async=False):
        duration = time.time() - _start_time
        ranked_processes = rank_attention(asmo.process._reflexes, asmo.process._non_reflexes)
        (_winners, actions, used_resources) = choose_winners(ranked_processes, [])
        asmo.process._reflexes = {}
        asmo.process._non_reflexes = {}
        series = {}
        # history does not need values from ranked_processes
        #   instead, it will also work with values from asmo.process._reflexes and asmo.process._non_reflexes
        #   however, processes used to determine the winners should be the same with processes used to record in history
        for (name, details) in ranked_processes:
            _history.setdefault(name, [])
            _history[name].append({'x': duration, 'y': details[asmo.configuration.total_attention_level_key]})
            series[name] = _history[name]
        return {'winners': _winners, 'actions': actions, 'used_resources': used_resources}
        
        
class WebAttention:
    def __init__(self, host):
        self.host = host
        
    def get_all_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, asmo.configuration.process_uri)
        return asmo.web_interface.get(uri, is_async)
        
    def get_reflex_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, asmo.configuration.process_uri)
        return asmo.web_interface.get(uri, is_async)
        
    def get_non_reflex_processes(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, asmo.configuration.process_uri)
        return asmo.web_interface.get(uri, is_async)
        
    def compete(self, is_async=False):
        uri = '{0}/{1}'.format(self.host, asmo.configuration.compete_uri)
        return asmo.web_interface.post(uri, {}, is_async)
        
        
def set_total_attention_level(dict_item):
    values = dict_item[1]
    values[asmo.configuration.total_attention_level_key] = values[asmo.configuration.attention_value_key] + values[asmo.configuration.boost_value_key]
    return values[asmo.configuration.total_attention_level_key]
    
def rank_attention(reflex_processes, non_reflex_processes):
    sorted_reflex = sorted(reflex_processes.items(), key=lambda x: x[1][asmo.configuration.priority_level_key], reverse=True)
    sorted_non_reflex = sorted(non_reflex_processes.items(), key=set_total_attention_level, reverse=True)
    return sorted_reflex + sorted_non_reflex
    
def choose_winners(ranked_processes, used_resources):
    winners = {}
    actions = {}
    
    for (name, details) in ranked_processes:
        # Check if required resources are available
        is_available = True
        for resource in details[asmo.configuration.required_resources_key]:
            if resource in used_resources:
                is_available = False
                break
                
        # Choose as a winner if required resources are available
        if is_available:
            used_resources.extend(details[asmo.configuration.required_resources_key])
            winners[name] = details
            actions.update(details[asmo.configuration.actions_key])
            
    return (winners, actions, used_resources)
    
def parse(options):
    parser = argparse.ArgumentParser(description="ASMO's Attention Mechanism")
    parser.add_argument('--local', action='store_true', help='Run ASMO locally')
    return parser.parse_args()
    
def run(attention, options):
    results = attention.compete()
    for (action, parameters) in results.get(asmo.configuration.actions_key, {}).items():
        arguments = shlex.split(action)
        arguments.append(json.dumps(parameters))
        p = subprocess.Popen(arguments)
    return True
    
def main(options):
    if parse(options).local:
        attention = LocalAttention(asmo.configuration.host)
        asmo.set_local_run()
    else:
        attention = WebAttention(asmo.configuration.host)
        asmo.set_web_run()
    print("[ OK ] Start ASMO's Attention Mechanism")
    while run(attention, options):
        time.sleep(asmo.configuration.competition_time)
        
if __name__ == '__main__':
    main({})
