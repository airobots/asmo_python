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
import tornado.httpserver
import tornado.ioloop

### ASMO ###

def calc_total_attention_level(attention_value, boost_value):
    return attention_value + boost_value
    
def rank_attention(process_dict):
    return sorted(process_dict.items(), key = lambda x: x[1]['attention_value'] + x[1]['boost_value'], reverse = True)
    
def choose_winners(ranked_processes, used_resources):
    winners = {}
    actions = {}
    
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
            actions.update(details['actions'])
            
    return (winners, actions, used_resources)
    
def post_process(process_dict, name, body):
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
                body['total_attention_level'] = calc_total_attention_level(body['attention_value'], body['boost_value'])
                
            process_dict[name] = body
            reply = {'ok': True}
        else:
            reply = {'error': error_msg}
            
    return (process_dict, reply)
    
### Web ###

# Sample:
# process_dict = {'name1': {'boost_value': 1, 'name': 'name1', 'attention_value': 10}, 'name2': {'boost_value': 5, 'name': 'name2', 'attention_value': 8}}
# curl -X POST http://localhost:12766/process/name1 -H 'content-type: application/json' --data '{"attention_value": 10, "boost_value": 1, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action1(0.2, 0.0, 0.0)"]}'
# curl -X POST http://localhost:12766/process/name2 -H 'content-type: application/json' --data '{"attention_value": 8, "boost_value": 5, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action2(-0.2, 0.0, 0.0)"]}'

class Application(tornado.web.Application):
    def __init__(self, options):
        self.process_dict = {}
        self.memory_dict = {}
        self.winners = {}
        self.start_time = 0
        self.history = {}
        tornado.web.Application.__init__(self, **options)
        
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", '*')
        
    @tornado.gen.coroutine
    def get(self, uri):
        if uri == 'favicon.ico':
            reply = {}
        elif uri == 'version':
            reply = {_application_name_: 'welcome', 'version': _version_}
        elif uri in ['process', 'process/']:
            reply = json.dumps(self.application.process_dict)
        elif uri == 'winners':
            reply = json.dumps(winners)
        else:
            reply = {'error': 'invalid url'}
            
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if uri == 'compete':
            duration = time.time() - self.application.start_time
            ranked_processes = rank_attention(self.application.process_dict)
            (self.application.winners, actions, used_resources) = choose_winners(ranked_processes, [])
            self.application.process_dict = {}
            series = {}
            # history does not need values from ranked_processes
            #   instead, it will also work with values from process_dict
            #   however, processes used to determine the winners should be the same with processes used to record in history
            for (name, details) in ranked_processes:
                self.application.history.setdefault(name, [])
                self.application.history[name].append({'x': duration, 'y': details['total_attention_level']})
                series[name] = self.application.history[name]
            reply = {'winners': self.application.winners, 'actions': actions, 'used_resources': used_resources}
        elif uri == 'reset_time':
            self.application.start_time = time.time()
            reply = {'ok', True}
        elif uri == 'reset_history':
            self.application.history = []
            reply = {'ok', True}
        else:
            reply = {'error': 'invalid url'}
            
        self.write(reply)
        
class ProcessHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'process {name} does not exist'.format(name=uri)}
        reply = json.dumps(self.application.process_dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if len(uri) > 0:
            body = json.loads(self.request.body.decode('utf-8'))
            (self.application.process_dict, reply) = post_process(self.application.process_dict, uri, body)
        else:
            reply = {'error': 'process name is empty'}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            self.application.process_dict.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'process {name} does not exist'.format(name=uri)}
            
        self.write(reply)
        
class MemoryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'memory {name} does not exist'.format(name=uri)}
        reply = json.dumps(self.application.memory_dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        self.application.memory_dict[uri] = json.loads(self.request.body.decode('utf-8'))
        reply = {'ok': True}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            self.application.memory_dict.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'memory {name} does not exist'.format(name=uri)}
        self.write(reply)
        
### Main ###

_application_name_ = 'Attentive Self-Modifying Architecture'
_version_ = '0.1'
_handlers = [
    (r'/client/(.*)', tornado.web.StaticFileHandler, {'path': 'client'}),
    (r'/process/(.*)', ProcessHandler),
    (r'/memory/(.*)', MemoryHandler),
    (r'/', tornado.web.RedirectHandler, {'url': 'client/index.html'}),
    (r'/(.*)', MainHandler),
]
_default_settings = {
    'server_address': '',
    'server_port': 12766,
    'handlers': _handlers,
}

def display_usage(default_settings):
    text =  'Usage: python3 {script_file} [OPTION]... \n\n'
    text += 'Example: \n'
    text += '  python3 {script_file} --address="{server_address}" --port={server_port} \n\n'
    text += 'Available options: \n'
    text += '  -h, --help               display this help and exit \n'
    text += '  -a, --address=ADDRESS    server IP address (default {server_address}) \n'
    text += '  -p, --port=PORT          server port (default {server_port}) \n'
    text = text.format(script_file = sys.argv[0], **default_settings)
    print(text)
    
def parse_options(default_settings):
    try:
        (options_and_values, arguments) = getopt.getopt(sys.argv[1:], 'ha:p:', ['help', 'address=', 'port='])
    except getopt.GetoptError as error:
        print(error)
        display_usage(default_settings)
        sys.exit(2)
    except:
        print(sys.exc_info()[0])
        raise
        
    options = dict(default_settings)
    
    for (option, value) in options_and_values:
        if option in ('-h', '--help'):
            display_usage(default_settings)
            sys.exit()
        elif option in ('-a', '--address'):
            options['server_address'] = value
        elif option in ('-p', '--port'):
            options['server_port'] = value
            
    return options
    
def main():
    options = parse_options(_default_settings)
    application = Application(options)
    server = tornado.httpserver.HTTPServer(application)
    application.listen(options['server_port'], address=options['server_address'])
    address_text = options['server_address']
    if address_text == '': address_text = 'localhost'
    print('Serving on {address}:{port}'.format(address=address_text, port=options['server_port']))
    application.start_time = time.time()
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
    main()
