#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
ASMO Local Controller
---------------------

Author:

* Rony Novianto (rony@ronynovianto.com)
"""

import shlex, asyncio, glob, importlib
from . import configuration, memory, process, attention

def set_local_run():
    configuration.is_running_local = True
    memory.Memory = memory.LocalMemory
    process.ReflexProcess = process.LocalReflexProcess
    process.NonReflexProcess = process.LocalNonReflexProcess
    
def set_web_run():
    configuration.is_running_local = False
    memory.Memory = memory.WebMemory
    process.ReflexProcess = process.WebReflexProcess
    process.NonReflexProcess = process.WebNonReflexProcess
    
    
class BaseController:
    def __init__(self):
        self.is_stop_requested = False
        
    async def on_compete_finish(self, results):
        async for (action, parameters) in results.get(configuration.actions_key, {}).items():
            arguments = shlex.split(action)
            arguments.append(json.dumps(parameters))
            p = subprocess.Popen(arguments)
        return True
        
    async def run(self, *args, **kwargs):
        pass
        
    async def keep_run(self, *args, **kwargs):
        is_run_requested = True
        while not self.is_stop_requested and is_run_requested:
            is_run_requested = await self.run(*args, **kwargs)
            await asyncio.sleep(configuration.competition_time)
            
    def stop(self):
        self.is_stop_requested = True
        
        
class LocalController(BaseController):
    def __init__(self, settings={}):
        self.processes = {}
        self.results = {}
        self.attention = attention.LocalAttention()
        self.settings = settings
        set_local_run()
        
    def on_load_error(self, filename):
        pass
        
    def load_processes(self, directory, is_skip_error=True):
        for filename in glob.glob(directory):
            (name_without_ext, _ext) = os.path.splitext(filename)
            module_name = os.path.basename(name_without_ext)
            try:
                specification = importlib.util.spec_from_file_location(module_name, filename)
                module = importlib.util.module_from_spec(specification)
                specification.loader.exec_module(module)
                process = module._init_(self.settings)
                self.processes[process.process_name] = process
            except (AttributeError, ImportError):
                self.on_load_error(filename)
                if not is_skip_error: break
                
    async def run(self, *args, **kwargs):
        is_run_requested = False
        async for process in self.processes.values():
            is_run_requested |= await process.run(*args, **kwargs)
        results = self.attention.compete()
        async for (name, details) in results['winners'].items():
            details[configuration.actions_key].get('_set_memory_')
            callback = details['actions'].get('_callback_')
            if callback:
                callback['function'](callback['arguments'])
        is_run_requested |= await self.on_compete_finish(results)
        return is_run_requested
        
        
class WebController(BaseController):
    def __init__(self, host=configuration.host):
        self.attention = attention.WebAttention(host)
        set_web_run()
        
    async def run(self, *args, **kwargs):
        results = self.attention.compete()
        return await self.on_compete_finish(results)
        
        
def parse_arguments():
    parser = argparse.ArgumentParser(description='ASMO')
    parser.add_argument('-l', '--local_processes_dir', nargs='+', help='Location of the local processes')
    return parser.parse_args()
    
def main(arguments):
    if arguments.local_processes_dir:
        controller = LocalController()
    else:
        controller = WebController(configuration.url)
    print('[ OK ] ASMO is running')
    try:
        asyncio.get_event_loop().run_until_complete(controller.keep_run())
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
        
if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)