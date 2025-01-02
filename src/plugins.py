import os
import sys
import importlib.util
import inspect
from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def event_load(self):
        """
        This method must be implemented by all plugins.
        This method will be called to initalize the plugin's behaviour
        """
        pass

    @abstractmethod
    def event_kill(self):
        """
        This method must be implemented by all plugins.
        This method will be called when the application exits
        """

    @abstractmethod
    def event_message(self, message):
        """
        This method must be implemented by all plugins.
        This method will be called when a message is recived
        """
        pass

    @abstractmethod
    def configure(self, config:dict):
        """
        This method must be implemented by all plugins.
        This method will be called to configure the plugins behaviour
        """
        pass

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        # Get the path of the current file (whether running as a script or compiled executable)
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Set the plugin directory relative to the base path
        self.plugin_dir = os.path.join(base_path, plugin_dir)
        self.plugins = []

    def load_plugins(self):
        if os.path.isdir(self.plugin_dir):
            for filename in os.listdir(self.plugin_dir):
                if filename.endswith(".py") and filename != "__init__.py":
                    self.load_plugin(filename)

    def load_plugin(self, filename):
        plugin_name = filename[:-3]  # Remove ".py" extension
        plugin_path = os.path.join(self.plugin_dir, filename)
        
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Find all classes that implement PluginInterface
        for name, obj in inspect.getmembers(plugin_module):
            if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                self.plugins.append(obj())

    def initalize_plugins(self):
        for plugin in self.plugins:
            plugin.event_load()

    def unload_plugins(self):
        for plugin in self.plugins:
            plugin.event_kill()
