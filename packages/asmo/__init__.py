#!/usr/bin/env python

import asmo.configuration
from asmo.attention import LocalAttention
from asmo.attention import WebAttention
from asmo.memory import Memory
from asmo.process import ReflexProcess
from asmo.process import NonReflexProcess

def is_running_local():
    return asmo.configuration.is_running_local
    
def set_local_run():
    asmo.configuration.is_running_local = True
    asmo.memory.Memory.read_data = asmo.memory.Memory._local_read_data
    asmo.memory.Memory.write_data = asmo.memory.Memory._local_write_data
    asmo.process.ReflexProcess.propose = asmo.process.ReflexProcess._local_propose
    asmo.process.NonReflexProcess.propose = asmo.process.NonReflexProcess._local_propose
    asmo.process.NonReflexProcess.propose_with_weights = asmo.process.NonReflexProcess._local_propose_with_weights
    
def set_web_run():
    asmo.configuration.is_running_local = False
    asmo.memory.Memory.read_data = asmo.memory.Memory._web_read_data
    asmo.memory.Memory.write_data = asmo.memory.Memory._web_write_data
    asmo.process.ReflexProcess.propose = asmo.process.ReflexProcess._web_propose
    asmo.process.NonReflexProcess.propose = asmo.process.NonReflexProcess._web_propose
    asmo.process.NonReflexProcess.propose_with_weights = asmo.process.NonReflexProcess._web_propose_with_weights
