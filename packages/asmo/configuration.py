#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Configuration
------------------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

import ntutil

# Run web to support any programming language via RESTful web service
# Run local if a higher performance is required (e.g. using ASMO with machine learning)
is_running_local = False
host = 'http://localhost:12766'
url = 'http://localhost:12766'

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

maximum_attention_value = 100.0
minimum_attention_value = 0.0


uri = ntutil.AttributeDict()
uri.memory = 'memory'
uri.process = 'process'
uri.compete = 'compete'

process_keys = ntutil.AttributeDict()
process_keys.priority_level = 'priority_level'
process_keys.total_attention_level = 'total_attention_level'
process_keys.attention_value = 'attention_value'
process_keys.boost_value = 'boost_value'
process_keys.required_resources = 'required_resources'
process_keys.actions = 'actions'

attention_value = ntutil.AttributeDict()
attention_value.minimum = 0.0
attention_value.maximum = 100.0