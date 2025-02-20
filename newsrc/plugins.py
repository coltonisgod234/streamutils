from typing import Protocol
import multiprocessing
import importlib.util
import inspect
import sys
import os

class PluginContainer:
    '''
    Container around a Plugin() and PluginHost()
    '''
    def __init__(self, host, queue, plugin):
        self.host = host
        self.hostqueue = queue
        self.plugin = plugin

class Plugin(Protocol):
    def startup(self, config:dict): ...
    def destroy(self): ...

    def message(self, message): ...

class PluginHost:
    '''
    Hosts a single plugin's process
    '''
    def __init__(self, queue, plugin):
        self.queue = queue
        self.running = False
        self.plugin = plugin
    
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
            return

        print("GOT EVENT:", event)
        if event.startswith("MESSAGESERIAL;"):
            obj = self.next_ev()
            self.plugin.message(obj)

        elif event.startswith("TERMINATE;"):
            self.running = False

    def start(self):
        '''
        Starts the pluginhost, usually a target for multiprocessing.Process()
        '''
        self.running = True
        while self.running:
            self.tick()
        
        return
    
    def stop(self):
        '''
        Stops the pluginhost
        '''
        self.running = False

class PluginExample:
    def startup(self, config):
        print("Plugin started up")
    
    def destroy(self):
        print("Plugin destroyed")
    
    def message(self, message):
        print("Plugin got message", message.stringified)

class PluginManager:
    '''
    Manages plugins
    '''
    def __init__(self, path):
        self.plugins = {}

    def find_plugin_class(self, module):
        '''
        Finds the first class in a given module that satisfies the `Plugin` interface
        '''
        for name, obj in inspect.getmembers(module, inspect.isclass):  # Loop through all members in the module
            if issubclass(obj, Plugin):  # Check if it satisfies the interface, then we can return it
                return obj

        return None  # If nothing satisfies it, then we return None

    def load_plugin(self, filename, path, config):
        '''
        Loads a specific plugin by calling it's startup() method
        '''
        spec = importlib.util.spec_from_file_location(filename, path)  # Create a spec from the filename and path
        module = importlib.util.module_from_spec(spec)  # Load that spec as a module
        plugin = self.find_plugin_class(module)  # Find the plugin within there
        if plugin is None:
            return None  # Makes sure that the class we want actually EXISTS

        queue = multiprocessing.Queue()
        host = PluginHost(queue, plugin)
        self.plugins[module.__qualname__] = PluginContainer(host, queue, plugin)

