import os
import sys
import importlib.util
import inspect
import pluginsdk
import json

class PluginManager:
    def __init__(self, plugin_dir="plugins", base_dir=os.path.abspath(__file__), signal=None, config=None):
        self.install_dir = base_dir
        self.plugin_dir = os.path.join(self.install_dir, plugin_dir)
        self.plugins = {}
        self.gui_signal = signal
        self.config = config

    def is_plugin_enabled(self, plugin_name):
        if self.config["Plugins.enable"][plugin_name] == "yes":
            return True
        else:
            return False
    
    def is_file_plugin(self, filename):
        if filename.endswith(".py") and filename != "__init__.py":
            return True
        else:
            return False
    
    def should_load_plugin(self, filename):
        return self.is_file_plugin(filename) and self.is_plugin_enabled(filename[:-3])

    def load_plugins(self, signal): 
        if not os.path.isdir(self.plugin_dir):
            return
        
        for filename in os.listdir(self.plugin_dir):
            if self.should_load_plugin(filename):
                # Load the plugin
                self.load_plugin(filename)

    def is_plugin_valid(self, obj):
        if inspect.isclass(obj) and issubclass(obj, pluginsdk.PluginInterface) and obj != pluginsdk.PluginInterface:
            return True
        else:
            return False

    def load_plugin(self, filename):
        plugin_name = filename[:-3]  # Remove ".py" extension
        json_path = f"{plugin_name}.json"  # Find the coresponding JSON
        plugin_path = os.path.join(self.plugin_dir, filename)
        
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Look at only the first member found
        members =  inspect.getmembers(plugin_module)
        for name, obj in members:
            if self.is_plugin_valid(obj):
                try:
                    o = obj()
                    o.__name__ = plugin_name
                    o.__file__ = plugin_path
                    o.__json__ = json_path
                    o.__signal__ = self.gui_signal
                    self.plugins[plugin_name] = o
                    #self.plugins[name].event_load()
                    self.gui_signal.emit(f"Plugin {plugin_name} is OK.")
                except Exception as e:
                    # Just skip loading it if the plugin errors
                    print(f"Error loading plugin {plugin_name}, unhandled exception: {e}")
                    self.gui_signal.emit(f"Error opening plugin {plugin_name}, caught exception: {e}")
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
