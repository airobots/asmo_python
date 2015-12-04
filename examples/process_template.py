#!/usr/bin/env python

'''
    Process_name
    -------------------------
    Process description
    
    Authors:
        First author (first author's email)
        Second author (second author's email)
'''

import asmo

def run(p):
    # See the documentation for naming conventions for reading paths, writing paths and resources
    reading_data = p.read_data('robot_name/path_to_read')
    # read_data() in the default sync mode returns dict()
    # e.g. reading_data = {'x': 1.0, 'y': 2.0, 'z': 3.0}
    if reading_data and 'error' not in reading_data:
        # Do some processing and store the processed data to ASMO's memory
        # process_data = ...
        p.write_data('robot_name/path_to_write', processed_data)
        p.actions = {
            'action1_name': action1_parameters,
            'action2_name': action2_parameters
        }
        p.required_resources = ['robot_name/resource1', 'robot_name/resource2', 'robot_name/resource3']
        p.propose(attention_value=0.0)
        
    # Return true to keep running or false to stop
    return True
    
def main():
    process = asmo.NonReflexProcess('http://localhost:12766', 'process_name', run)
    print('[ OK ] Start {0}'.format(process.process_name))
    while run(process): pass
    
if __name__ == '__main__':
    main()
