from typing import Protocol, runtime_checkable
import multiprocessing
import importlib.util
import importlib
import inspect
import sys
from time import sleep, time_ns
import os

from events import events

@runtime_checkable
class Plugin(Protocol):
    def startup(self, config:dict): ...
    def destroy(self): ...

    def nullevent(self): ...
    def message(self, message): ...

class PluginHost:
    '''
    Hosts a single plugin's process
    '''
    def __init__(self, queue, plugin):
        self.queue = queue
        self.process = None
        self.running = False
        self.plugin = plugin
        self.plugin_name = type(self.plugin).__name__
    
    def next_ev(self):
        '''
        Returns the next event from queue.get()
        '''
        if not self.queue.empty():
            event = self.queue.get(False)
            return event
        else:
            return ""
    
    def tick(self):
        '''
        Processes one event from the queue
        '''
        event = self.next_ev()
        if event == "":
            self.plugin.nullevent()
            return

        if event.startswith(events.PICKLEDMESSAGE.value):
            obj = self.next_ev()
            self.plugin.message(obj)

        elif event.startswith(events.TERMINATE.value):
            self.running = False

    def start(self, config):
        '''
        Starts the pluginhost, usually a target for multiprocessing.Process()
        '''
        self.running = True

        self.plugin.startup(config)
        while self.running:
            self.tick()
        
        return
    
    def stop(self):
        self.running = False
        self.plugin.destroy()

    def mpbegin(self, config):
        '''
        Create a multiprocessing instance and call start()
        '''
        self.process = multiprocessing.Process(target=self.start, args=(config,))
        self.process.start()
        return
    
    def mpstop(self):
        self.stop()

        self.queue.put_nowait(events.TERMINATE.value)
        self.process.join()
        return
    
    def send_event(self, event):
         self.queue.put_nowait(event)

class PluginManager:
    '''
    Manages plugins
    '''
    def __init__(self, path, pluginprotocol=Plugin):
        self.plugins: dict[PluginContainer] = {}
        self.pluginprotocol = pluginprotocol

    def find_plugin_class(self, module):
        '''
        Finds the first class in a given module that satisfies the `Plugin` interface
        '''
        
        members = inspect.getmembers(module, inspect.isclass)
        for name, obj in members:
            if issubclass(obj, self.pluginprotocol):
                return obj
        return None

    def mem_load_plugin(self, plugin, name):
        queue = multiprocessing.Queue()
        host = PluginHost(queue, plugin)
        self.plugins[name] = host

    def disk_load_plugin(self, filename, path):
        '''
        Loads a specific plugin but does not start it
        '''
        spec = importlib.util.spec_from_file_location(filename, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        plugin = self.find_plugin_class(module)
        if plugin is None:
            return None

        loadedplugin = plugin()

        self.mem_load_plugin(loadedplugin, filename)

    def start_plugin(self, name, config):
        self.plugins[name].mpbegin(config)
    
    def stop_plugin(self, name):
        self.plugins[name].mpstop()
    
    def send_event(self, name, event):
        self.plugins[name].send_event(event)

mgr = PluginManager("plugins")
mgr.disk_load_plugin("example.py", "/mnt/sda1/streamutils2/newsrc/plugins/example.py")
mgr.start_plugin("example.py", {})

sleep(1)

mgr.stop_plugin("example.py")



exit(1)