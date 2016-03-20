#!/usr/bin/env python

'''
    ASMO Configuration
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

# Run web to support any programming language via RESTful web service
# Run local if a higher performance is required (e.g. using ASMO with machine learning)
is_running_local = False
host = 'http://localhost:12766'

# Memory
memory_uri = 'memory'

# Attention
process_uri = 'process'
compete_uri = 'compete'
competition_time = 0.5

priority_level_key = 'priority_level'
total_attention_level_key = 'total_attention_level'
attention_value_key = 'attention_value'
boost_value_key = 'boost_value'
required_resources_key = 'required_resources'
actions_key = 'actions'
