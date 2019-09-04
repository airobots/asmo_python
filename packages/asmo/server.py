#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Server
-----------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

import argparse, urllib, time, json
import tornado.web, tornado.ioloop, asmo

'''
Examples:
non_reflex = {'name1': {'boost_value': 1, 'name': 'name1', 'attention_value': 10}, 'name2': {'boost_value': 5, 'name': 'name2', 'attention_value': 8}}
curl -X POST http://localhost:12766/process/name1 -H 'content-type: application/json' --data '{"attention_value": 10, "boost_value": 1, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action1(0.2, 0.0, 0.0)"]}'
curl -X POST http://localhost:12766/process/name2 -H 'content-type: application/json' --data '{"attention_value": 8, "boost_value": 5, "required_resources": ["/leg/left", "/leg/right"], "actions": ["action2(-0.2, 0.0, 0.0)"]}'
'''
class Application(tornado.web.Application):
    _name_ = 'Attentive Self-Modifying Architecture (ASMO) Server'
    _version_ = '0.1'
    
    def __init__(self, settings):
        self.settings = settings
        self.attention = asmo.attention.LocalAttention('')
        super().__init__([
            (r'/client/(.*)', tornado.web.StaticFileHandler, {'path': 'client'}),
            (r'/process/(.*)'.format(asmo.configuration.process_uri), ProcessHandler),
            (r'/memory/(.*)'.format(asmo.configuration.memory_uri), MemoryHandler),
            (r'/', tornado.web.RedirectHandler, {'url': 'client/index.html'}),
            (r'/(.*)', MainHandler),
        ])
        
        
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", '*')
        
    @tornado.gen.coroutine
    def get(self, uri):
        if uri == 'favicon.ico':
            reply = {}
        elif uri == 'version':
            reply = {'name': self.application._name_, 'version': self.application._version_}
        elif uri in ['process', 'process/']:
            processes = self.application.attention.get_all_processes()
            reply = json.dumps(processes)
        elif uri == 'winners':
            reply = json.dumps(asmo.attention._winners)
        else:
            reply = {'_error': 'invalid url'}
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if uri == 'compete':
            reply = self.application.attention.compete()
        elif uri == 'reset_time':
            asmo.attention._start_time = time.time()
            reply = {'_ok': True}
        elif uri == 'reset_history':
            asmo.attention._history = {}
            reply = {'_ok': True}
        else:
            reply = {'_error': 'invalid url'}
        self.write(reply)
        
        
class ProcessHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'_error': 'process {name} does not exist'.format(name=uri)}
        non_reflex = asmo.process._non_reflexes.get(uri, default)
        reflex = asmo.process._reflexes.get(uri, non_reflex)
        reply = json.dumps(reflex)
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        if not uri:
            reply = {'_error': 'process name is empty'}
        else:
            body = json.loads(self.request.body.decode('utf-8'))
            required_keys = set([asmo.configuration.priority_level_key, asmo.configuration.attention_value_key, asmo.configuration.boost_value_key, asmo.configuration.required_resources_key, asmo.configuration.actions_key])
            keys_difference = required_keys - set(body.keys())
            if keys_difference == set([asmo.configuration.attention_value_key, asmo.configuration.boost_value_key]):
                # Reflex process
                body['name'] = uri
                asmo.process._reflexes.setdefault(uri, {})
                asmo.process._reflexes[uri].update(body)
                reply = {'_ok': True}
            elif keys_difference == set([asmo.configuration.priority_level_key]):
                # Non-reflex process
                body['name'] = uri
                asmo.attention.set_total_attention_level((uri, body))
                asmo.process._non_reflexes.setdefault(uri, {})
                asmo.process._non_reflexes[uri].update(body)
                reply = {'_ok': True}
            else:
                # Incomplete data
                reply = {'_error': error_msg}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            if uri in asmo.process._reflex:
                asmo.process._reflex.pop(uri)
            else:
                asmo.process._non_reflex.pop(uri)
            reply = {'_ok': True}
        except KeyError:
            reply = {'_error': 'process {name} does not exist'.format(name=uri)}
        self.write(reply)
        
        
class MemoryHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, uri):
        default = {'_error': 'memory {name} does not exist'.format(name=uri)}
        reply = json.dumps(asmo.memory._dict.get(uri, default))
        self.write(reply)
        
    @tornado.gen.coroutine
    def post(self, uri):
        asmo.memory._dict[uri] = json.loads(self.request.body.decode('utf-8'))
        reply = {'_ok': True}
        self.write(reply)
        
    @tornado.gen.coroutine
    def delete(self, uri):
        try:
            asmo.memory._dict.pop(uri)
            reply = {'_ok': True}
        except KeyError:
            reply = {'_error': 'memory {name} does not exist'.format(name=uri)}
        self.write(reply)
        
        
def parse_arguments():
    parser = argparse.ArgumentParser(description='{name} {version}'.format(name=Application._name_, version=Application._version_))
    parser.add_argument('-u', '--url', default='http://0.0.0.0:12766', help='URL to serve', dest='url')
    return parser.parse_args()
    
def main(arguments):
    settings = arguments.__dict__
    application = Application(settings)
    parsed_url = urllib.parse.urlparse(settings['url'])
    application.listen(parsed_url.port, address=parsed_url.hostname)
    print('[ OK ] {name} is running on {url}'.format(name=application._name_, url=settings['url']))
    tornado.ioloop.IOLoop.current().start()
    
if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)