#!/usr/bin/python

'''
    ASMO Server
    -----------
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import sys
import getopt
import time
import json
import tornado.web
import tornado.ioloop

__application_name__ = 'Attentive Self-Modifying Architecture'
__version__ = '0.1'
ip_address = ''
port = 12766

process_dict = {}
memory_dict = {}
winners = {}
start_time = 0
history = {}

### ASMO ###

def calc_total_attention_level(attention_value, boost_value):
    return attention_value + boost_value
    
def rank_attention(process_dict):
    return sorted(process_dict.items(), key = lambda x: x[1]['attention_value'] + x[1]['boost_value'], reverse = True)
    
def choose_winners(ranked_processes, used_resources):
    global winners
    winners = {}
    actions = []
    
    for (name, details) in ranked_processes:
        # Check if required resources are available
        is_available = True
        for resource in details['required_resources']:
            if resource in used_resources:
                is_available = False
                break
                
        # Choose as a winner if required resources are available
        if is_available:
            used_resources.extend(details['required_resources'])
            winners[name] = details
            actions.extend(details['actions'])
            
    return (winners, actions, used_resources)
    
def post_process(name, body):
    if name in process_dict:
        # Update existing process
        process_dict[name].update(body)
        reply = {'ok': True}
    else:
        # Add new process
        if 'priority_level' in body:
            # reflex
            required_keys = ['actions', 'required_resources', 'priority_level']
            error_msg = 'missing actions, resources or priority level'
        else:
            # non-reflex
            required_keys = ['actions', 'required_resources', 'attention_value', 'boost_value']
            error_msg = 'missing actions, resources, attention value or boost value'
            
        is_complete = True
        for key in required_keys:
            if key not in body:
                is_complete = False
                break
                
        if is_complete:
            body['name'] = name
            if 'priority_level' not in body:
                body['total_attention_level'] = body['attention_value'] + body['boost_value']
            process_dict[name] = body
            reply = {'ok': True}
        else:
            reply = {'error': error_msg}
            
    return reply
    
### Web ###

# Sample:
# process_dict = {'chase_ball': {'boost_value': 1, 'name': 'chase_ball', 'attention_value': 10}, 'return_defense': {'boost_value': 5, 'name': 'return_defense', 'attention_value': 8}}
# curl -X PUT http://localhost:8000/process/chase_ball -H 'content-type: application/json' --data '{"attention_value": 10, "boost_value": 1, "required_resources": ["/leg/left", "/leg/right"], "actions": ["chase_ball(0.2, 0.0, 0.0)"]}'
# curl -X PUT http://localhost:8000/process/return_defense -H 'content-type: application/json' --data '{"attention_value": 8, "boost_value": 5, "required_resources": ["/leg/left", "/leg/right"], "actions": ["return_defense(-0.2, 0.0, 0.0)"]}'
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", '*')
        
    @tornado.gen.coroutine
    def get(self, uri):
        if uri == 'favicon.ico':
            reply = {}
        elif uri == 'version':
            reply = {application_name: 'welcome', 'version': __version__}
        elif uri == 'process' or uri == 'process/':
            reply = json.dumps(process_dict)
        elif uri == 'winners':
            reply = json.dumps(winners)
        else:
            reply = {'error': 'invalid url'}
            
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        global start_time, history, process_dict
        if uri == 'compete':
            duration = time.time() - start_time
            ranked_processes = rank_attention(process_dict)
            (winners, actions, used_resources) = choose_winners(ranked_processes, [])
            process_dict = {}
            series = {}
            # history does not need values from ranked_processes
            #   instead, it will also work with values from process_dict
            #   however, processes used to determine the winners should be the same with processes used to record in history
            for (name, details) in ranked_processes:
                history.setdefault(name, [])
                total_attention_level = calc_total_attention_level(details['attention_value'], details['boost_value'])
                history[name].append({'x': duration, 'y': total_attention_level})
                series[name] = history[name]
            reply = {'winners': winners, 'actions': actions, 'used_resources': used_resources}
        elif uri == 'reset_time':
            start_time = time.time()
            reply = {'ok', True}
        elif uri == 'reset_history':
            history = []
            reply = {'ok', True}
        else:
            reply = {'error': 'invalid url'}
            
        self.write(reply)
        
class ProcessHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'process {name} does not exist'.format(name=uri)}
        reply = json.dumps(process_dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if len(uri) > 0:
            body = json.loads(self.request.body.decode('utf-8'))
            reply = post_process(uri, body)
        else:
            reply = {'error': 'process name is empty'}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            process_dict.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'process {name} does not exist'.format(name=uri)}
            
        self.write(reply)
        
class MemoryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'memory {name} does not exist'.format(name=uri)}
        reply = json.dumps(memory_dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        memory_dict[uri] = json.loads(self.request.body.decode('utf-8'))
        reply = {'ok': True}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            memory_dict.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'memory {name} does not exist'.format(name=uri)}
        self.write(reply)
        
config = [
    (r'/client/(.*)', tornado.web.StaticFileHandler, {'path': 'client'}),
    (r'/process/(.*)', ProcessHandler),
    (r'/memory/(.*)', MemoryHandler),
    (r'/', tornado.web.RedirectHandler, {'url': 'client/index.html'}),
    (r'/(.*)', MainHandler),
]

### Main ###

def display_usage():
    text =  'Usage: python3 {script_file} [OPTION]... \n\n'
    text += 'Example: \n'
    text += '  python3 {script_file} --address="0.0.0.0" --port={port} \n\n'
    text += 'Available options: \n'
    text += '  -h, --help               display this help and exit \n'
    text += '  -a, --address=ADDRESS    address \n'
    text += '  -p, --port=PORT          port \n'
    text = text.format(script_file = sys.argv[0], port = port)
    print(text)
    
def main():
    global ip_address, port
    
    try:
        (options_and_values, arguments) = getopt.getopt(sys.argv[1:], 'ha:p:', ['help', 'address=', 'port='])
    except getopt.GetoptError as err:
        print(err)
        display_usage()
        sys.exit(2)
        
    for (option, value) in options_and_values:
        if option in ('-h', '--help'):
            display_usage()
            sys.exit()
        elif option in ('-a', '--address'):
            ip_address = value
        elif option in ('-p', '--port'):
            port = value
            
    application = tornado.web.Application(config)
    application.listen(port, address=ip_address)
    address_text = ip_address
    if address_text == '': address_text = 'localhost'
    print('Serving on {address}:{port}'.format(address=address_text, port=port))
    start_time = time.time()
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
    main()
