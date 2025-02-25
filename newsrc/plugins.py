from typing import Protocol, runtime_checkable
import multiprocessing
import importlib.util
import importlib
import inspect
import sys
from time import sleep, time_ns
import os
import queue

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
        self.plugin = plugin
        self.plugin_name = type(self.plugin).__name__
        self.running = multiprocessing.Value('b', False)  # Shared boolean flag

    def next_ev(self):
        '''
        Returns the next event from queue.get()
        '''
        try:
            return self.queue.get_nowait()
        except queue.Empty:
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
            self.running.value = False  # Ensure shared state update

    def start(self, config):
        '''
        Starts the pluginhost, usually a target for multiprocessing.Process()
        '''
        self.running.value = True  # Shared flag
        self.plugin.startup(config)

        while self.running.value:
            self.tick()
            time.sleep(0.01)  # Avoid CPU overuse
        
        self.plugin.destroy()

    def stop(self):
        '''
        Stops the pluginhost process
        '''
        if self.process and self.process.is_alive():
            self.queue.put_nowait(events.TERMINATE.value)
            self.process.join(timeout=5)

            if self.process.is_alive():
                print(f"WARNING: Plugin {self.plugin_name} did not terminate, force killing.")
                self.process.terminate()  # Force kill if necessary
            
            self.process = None  # Cleanup
        else:
            print(f"Plugin {self.plugin_name} already stopped.")

    def mpbegin(self, config):
        '''
        Create a multiprocessing instance and call start()
        '''
        if self.process and self.process.is_alive():
            print(f"Plugin {self.plugin_name} is already running.")
            return

        self.process = multiprocessing.Process(target=self.start, args=(config,))
        self.process.start()

    def mpstop(self):
        '''
        Stops the multiprocessing instance
        '''
        self.stop()

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
