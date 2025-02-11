import os
import sys
import importlib.util
import inspect
import pluginsdk
import json

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.plugin_dir = os.path.join(base_path, plugin_dir)
        self.plugins = {}

    def load_plugins(self, signal): 
        if os.path.isdir(self.plugin_dir):
            for filename in os.listdir(self.plugin_dir):
                # For every file in the plugins directory
                # Load the corresponding plugin
                if filename.endswith(".py") and filename != "__init__.py":
                    # Load the plguin
                    self.load_plugin(filename)
                    signal.emit(f"Loaded {name}")

    def load_plugin(self, filename):
        plugin_name = filename[:-3]  # Remove ".py" extension
        json_path = f"{plugin_name}.json"  # Find the coresponding JSON
        plugin_path = os.path.join(self.plugin_dir, filename)
        
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Find all classes that implement PluginInterface
        for name, obj in inspect.getmembers(plugin_module):
            if inspect.isclass(obj) and issubclass(obj, pluginsdk.PluginInterface) and obj != pluginsdk.PluginInterface:
                try:
                    o = obj()
                    o.__name__ = plugin_name
                    o.__file__ = plugin_path
                    o.__json__ = json_path
                    self.plugins[name] = o
                    #self.plugins[name].event_load()
                except Exception as e:
                    # Just skip loading it if the plugin errors
                    print(f"Error loading plugin {name}, unhandled exception: {e}")
                    continue

    def configure_plugin(self, json_filename, plugin):
        file = os.path.join(self.plugin_dir, json_filename)
        with open(file, "r") as f:
            data = json.load(f)
            plugin.configure(data)

    def configure_plugins(self, signal):
        for name, plugin in self.plugins.items():
            self.configure_plugin(plugin.__json__, plugin)
            signal.emit(f"Configured {name}")

    def initalize_plugins(self, signal):
        for name, plugin in self.plugins.items():
            plugin.event_load()
            signal.emit(f"Initalized {name}")

    def unload_plugins(self):
        for plugin in self.plugins:
            plugin.event_kill()

    def notify(self, source:str | None, dest:str, data:str):
        self.plugins[dest].event_notify(source, data)
