#!/usr/bin/env python

'''
    Custom controller
    -------------------------
    This example shows how to build a custom controller
    
    Authors:
        Rony Novianto (rony@ronynovianto.com)
'''

import glob
import time
import asmo

def reinit_processes(directory, options):
    processes = {}
    filenames = glob.glob('*.py')
    for filename in filenames:
        try:
            module_name = filename[:-3].replace('/', '.')
            process = __import__(module_name, fromlist=['']).init(options)
            processes[process.process_name] = process
        except (AttributeError, ImportError):
            print('[ Error ] cannot initialize {filename}'.format(filename=filename))
            continue
        except Exception as e:
            raise
    return processes
    
def run(attention, processes, options):
    is_keep_running = False
    for process in processes.values():
        is_keep_running |= process.run(process, options)
    results = attention.compete()
    for (name, details) in results['winners'].items():
        print(name, details['total_attention_level'])
    for (action_name, parameter) in results['actions'].items():
        print(action_name, parameter)
    return is_keep_running
    
def main(options):
    asmo.set_local_run()
    attention = asmo.LocalAttention('attention_name')
    print('[ OK ] Start custom_controller')
    processes = reinit_processes('', options)
    while run(attention, processes, options): time.sleep(0.5)
    
if __name__ == '__main__':
    main({})
