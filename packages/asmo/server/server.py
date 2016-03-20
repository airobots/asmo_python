#!/usr/bin/python

'''
    ASMO Server
    -----------
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import sys
import getopt
import argparse
import time
import json
import tornado.web
import tornado.httpserver
import tornado.ioloop

import asmo

### ASMO ###

def post_process(name, body):
    required_keys = set([asmo.configuration.priority_level_key, asmo.configuration.attention_value_key, asmo.configuration.boost_value_key, asmo.configuration.required_resources_key, asmo.configuration.actions_key])
    keys_difference = required_keys - set(body.keys())
    if keys_difference == set([asmo.configuration.attention_value_key, asmo.configuration.boost_value_key]):
        # Reflex process
        body['name'] = name
        asmo.process._reflexes.setdefault(name, {})
        asmo.process._reflexes[name].update(body)
        reply = {'ok': True}
    elif keys_difference == set([asmo.configuration.priority_level_key]):
        # Non-reflex process
        body['name'] = name
        asmo.attention.set_total_attention_level((name, body))
        #body[asmo.configuration.total_attention_level_key] = asmo.attention.set_total_attention_level(body[asmo.configuration.attention_value_key], body[asmo.configuration.boost_value_key])
        asmo.process._non_reflexes.setdefault(name, {})
        asmo.process._non_reflexes[name].update(body)
        reply = {'ok': True}
    else:
        # Incomplete data
        reply = {'error': error_msg}
        
    '''
    # Add new process
    if 'priority_level' in body:
        # reflex
        required_keys = set(['actions', 'required_resources', 'priority_level'])
        error_msg = 'missing actions, resources or priority level'
    else:
        # non-reflex
        required_keys = set(['actions', 'required_resources', 'attention_value', 'boost_value'])
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
    '''
    return reply
    
### Web ###

# Sample:
# non_reflex = {'name1': {'boost_value': 1, 'name': 'name1', 'attention_value': 10}, 'name2': {'boost_value': 5, 'name': 'name2', 'attention_value': 8}}
# curl -X POST http://localhost:12766/process/name1 -H 'content-type: application/json' --data '{"attention_value": 10, "boost_value": 1, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action1(0.2, 0.0, 0.0)"]}'
# curl -X POST http://localhost:12766/process/name2 -H 'content-type: application/json' --data '{"attention_value": 8, "boost_value": 5, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action2(-0.2, 0.0, 0.0)"]}'

class Application(tornado.web.Application):
    def __init__(self, options):
        tornado.web.Application.__init__(self, **options)
        self.attention = asmo.attention.LocalAttention('')
        
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
            processes = self.application.attention.get_all_processes()
            reply = json.dumps(processes)
        elif uri == 'winners':
            reply = json.dumps(asmo.attention._winners)
        else:
            reply = {'error': 'invalid url'}
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if uri == 'compete':
            reply = self.application.attention.compete()
        elif uri == 'reset_time':
            asmo.attention._start_time = time.time()
            reply = {'ok', True}
        elif uri == 'reset_history':
            asmo.attention._history = {}
            reply = {'ok', True}
        else:
            reply = {'error': 'invalid url'}
        self.write(reply)
        
class ProcessHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'process {name} does not exist'.format(name=uri)}
        non_reflex = asmo.process._non_reflexes.get(uri, default)
        reflex = asmo.process._reflexes.get(uri, non_reflex)
        reply = json.dumps(reflex)
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
            if uri in asmo.process._reflex:
                asmo.process._reflex.pop(uri)
            else:
                asmo.process._non_reflex.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'process {name} does not exist'.format(name=uri)}
        self.write(reply)
        
class MemoryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'memory {name} does not exist'.format(name=uri)}
        reply = json.dumps(asmo.memory._dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        asmo.memory._dict[uri] = json.loads(self.request.body.decode('utf-8'))
        reply = {'ok': True}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            asmo.memory._dict.pop(uri)
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
    
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default='', type=str)
    parser.add_argument('-p', '--port', default=12766, type=int)
    return parser.parse_args()
    
def main(arguments):
    options = parse_options(_default_settings)
    application = Application(options)
    server = tornado.httpserver.HTTPServer(application)
    application.listen(options['server_port'], address=options['server_address'])
    address_text = options['server_address']
    if address_text == '': address_text = 'localhost'
    print('Serving on {address}:{port}'.format(address=address_text, port=options['server_port']))
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
