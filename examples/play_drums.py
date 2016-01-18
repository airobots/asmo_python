#!/usr/bin/env python

'''
    Play drums
    -------------------------
    This process first perceives the location of the drums and then look at the drums and beat the drums.
    
    Authors:
        Rony Novianto (rony@ronynovianto.com)
'''

import asmo

def determine_arms_positions(drums_position):
    arms_positions = None
    # Do some processing
    return arms_positions
    
def run(self, options):
    drums_position = self.read_data('smokey/visual/drums/position')
    if drums_position and 'error' not in drums_position:
        arms_positions = determine_arms_positions(drums_position)
        self.write_data('smokey/play_drums/arms_positions', arms_positions)
        self.actions = {
            'echo move_head': drums_position,
            'echo move_arms': arms_positions
        }
        self.required_resources = ['smokey/head', 'smokey/arms/left', 'smokey/arms/right']
        self.propose(attention_value=50.0)
    return True
    
def init(options):
    # Assume another process recognizes drums from images and stores the drums position to ASMO's memory
    memory = asmo.Memory('http://localhost:12766')
    memory.write_data('smokey/visual/drums/position', {'x': 1.0, 'y': 2.0, 'z': 3.0})
    process = asmo.NonReflexProcess('http://localhost:12766', 'play_drums', run)
    print('[ OK ] Start {0}'.format(process.process_name))
    return process
    
def main(options):
    process = init(options)
    while process.run(process, options): pass
    
if __name__ == '__main__':
    main({})
