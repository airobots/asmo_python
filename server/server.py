#!/usr/bin/python

'''
    ASMO Server
    Author:
        Rony Novianto (rony@ronynovianto.com)
'''

import sys
import getopt
import time
import tornado.web
import tornado.ioloop
import json

application_name = 'ASMO'
version = '0.1'
process_dict = {}
memory_dict = {}
winners = {}
start_time = 0
history = {}

def usage(name):
    print('python', name, '--hostname=[hostname] --port=[port]')
    
### ASMO ###

def calc_total_attention_level(attention_value, boost_value):
    return attention_value + boost_value
    
def rank_attention(process_dict):
    return sorted(process_dict.items(), key = lambda x: x[1]['attention_value'] + x[1]['boost_value'], reverse = True)
    
def choose_winners(ranked_processes, used_resources):
    #winners = []
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
            #winners.append((name, details))
            actions.extend(details['actions'])
            
    return (winners, actions, used_resources)
    
def post_non_reflex(name, body):
    if name not in process_dict:
        # Add new process
        if body.get('attention_value') == None or body.get('boost_value') == None or body.get('actions') == None or body.get('required_resources') == None:
            reply = {'error': 'missing attention value, boost value, actions or required resources'}
        else:
            body['name'] = name
            process_dict[name] = body
            reply = {'ok': True}
    elif body.get('attention_value') == None and body.get('boost_value') == None and body.get('actions') == None and body.get('required_resources') == None:
        reply = {'error': 'missing attention value, boost value, actions and required resources'}
    else:
        # Update existing process
        if body.get('attention_value') != None:
            process_dict[name]['attention_value'] = body['attention_value']
        if body.get('boost_value') != None:
            process_dict[name]['boost_value'] = body['boost_value']
        if body.get('actions') != None:
            process_dict[name]['actions'] = body['actions']
        if body.get('required_resources') != None:
            process_dict[name]['required_resources'] = body['required_resources']
        reply = {'ok': True}
        
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
            reply = {application_name: 'welcome', 'version': version}
        elif uri == 'process' or uri == 'process/':
            reply = json.dumps(process_dict)
        elif uri == 'winners':
            reply = json.dumps(winners)
        else:
            reply = {'error': 'invalid url'}
            
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        global start_time, history
        if uri == 'compete':
            duration = time.time() - start_time
            ranked_processes = rank_attention(process_dict)
            (names, actions, used_resources) = choose_winners(ranked_processes, [])
            series = {}
            # history does not need values from ranked_processes
            #   instead, it will also work with values from process_dict
            #   however, processes used to determine the winners should be the same with processes used to record in history
            for (name, details) in ranked_processes:
                history.setdefault(name, [])
                total_attention_level = calc_total_attention_level(details['attention_value'], details['boost_value'])
                history[name].append({'x': duration, 'y': total_attention_level})
                series[name] = history[name]
            #reply = {'names': names, 'actions': actions, 'used_resources': used_resources, 'series': series}
            reply = {'names': names, 'actions': actions, 'used_resources': used_resources}
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
        default = {'error': 'process {0} does not exist'.format(uri)}
        reply = json.dumps(process_dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        body = json.loads(self.request.body.decode('utf-8'))
        reply = post_non_reflex(uri, body)
        print(process_dict)
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            process_dict.pop(uri)
            reply = {'ok': True}
        except KeyError:
            reply = {'error': 'process {0} does not exist'.format(name)}
            
        self.write(reply)
        
class MemoryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'error': 'memory {0} does not exist'.format(uri)}
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
            reply = {'error': 'memory {0} does not exist'.format(uri)}
        self.write(reply)
        
config = [
    (r'/client/(.*)', tornado.web.StaticFileHandler, {'path': 'client'}),
    (r'/non_reflex/(.*)', ProcessHandler),
    (r'/reflex/(.*)', ProcessHandler),
    (r'/memory/(.*)', MemoryHandler),
    (r'/', tornado.web.RedirectHandler, {'url': 'client/index.html'}),
    (r'/(.*)', MainHandler),
]

### Main ###

if __name__ == '__main__':
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hn:p:', ['help', 'hostname=', 'port='])
    except getopt.GetoptError as err:
        print(str(err))
        usage(sys.argv[0])
        sys.exit(2)
        
    hostname = ''
    port = 12766
    
    for (opt, arg) in opts:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ('-n', '--hostname'):
            hostname = arg
        elif opt in ('-p', '--port'):
            port = arg
            
    application = tornado.web.Application(config)
    application.listen(port)
    print('Serving on port:', port)
    start_time = time.time()
    tornado.ioloop.IOLoop.instance().start()
