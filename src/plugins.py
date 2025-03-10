import os
import concurrent.futures as cf
import importlib.util
import inspect
import pluginsdk
import json
import types

class PluginManager:
    '''
    Class to manage plugins
    '''
    def __init__(self, plugin_dir="plugins", base_dir=os.path.abspath(__file__), signal=None, config=None):
        # Directory the program is installed in
        self.install_dir = base_dir  

        # Directory to load plugins from
        self.plugin_dir = os.path.join(self.install_dir, plugin_dir)

        # To hold plugins, key is the name of the plugin, value is the object
        self.plugins = {}

        # Signal to send information back to the GUI
        self.gui_signal = signal

        # Configure this class
        self.config = config

        # Maximum number of works that the executor can use
        self.max_workers = int(config["Plugins"]["max_workers"])

        # UNUSED
        self.use_threads = "threads"  # Hardcoding, TODO: I'll do this functionality later!

        # Prevent plugins from using too many threads
        self.plugin_blame = {}

        # Maximum blame any single plugin can have
        self.max_blame = int(self.config["Plugins"]["max_blame"])

        # What to do when there's too much blame
        self.blame_action = self.config["Plugins"]["blame_action"]

        # Execute plugins in paralel
        self.executor = cf.ThreadPoolExecutor(max_workers=self.max_workers)

        print(f"[PLUGIN MANAGER | INFO] concurent.futures has spawned a {self.use_threads}-based executor with {self.max_workers} workers.")

    def is_plugin_enabled(self, plugin_name):
        '''
        Returns True is a plugin is enabled in the config and False if it is not
        '''
        return self.config["Plugins.enable"].getboolean(plugin_name)
    
    def is_file_plugin(self, filename):
        '''
        Returns True if a given filename is a plugin anf False otherwise
        '''
        if filename.endswith(".py") and filename != "__init__.py":
            return True
        else:
            return False
    
    def should_load_plugin(self, filename):
        '''
        Returns True if a given filename should be loaded under the current config
        '''
        if self.is_file_plugin(filename) and self.is_plugin_enabled(filename[:-3]):
            return True
        else:
            return False

    def load_plugins(self):
        '''
        Load all valid plugins from the plugin directory
        '''
        if not os.path.isdir(self.plugin_dir):
            return
        
        # Loop through all the plugins
        for filename in os.listdir(self.plugin_dir):
            if self.should_load_plugin(filename):  # If we should load it
                # Load the plugin
                self.load_plugin(filename)

    def is_plugin_valid(self, obj):
        '''
        Check if a given plugin object is a valid plugin and not some random object
        '''
        if inspect.isclass(obj) and issubclass(obj, pluginsdk.PluginInterface) and obj != pluginsdk.PluginInterface:
            return True
        else:
            return False
        
    def plugin_done_function(self, future:cf.Future, name:str):
        '''
        Required to manage blame.
        Runs when a given plugin is done executing
        '''
        self.plugin_blame[name] -= 1
        print(f"[PLUGIN MANAGER | DEBUG] {name}'s blame is {self.plugin_blame[name]} (max {self.max_blame})")
    
    def plugin_run_function(self, plugin_name:str, function_name:str, args:tuple=()):
        '''
        Run a given function from a plugin
        '''
        # Ensure the executor is still alive and hasn't terminated
        if self.executor._shutdown:
            print(f"[PLUGIN MANAGER | ERROR] Attempted to start a new task on {self.use_threads}-based executor after it's shutdown! Ignoring request.")
            print("[PLUGIN MANAGER | NOTE] ^^^ The above error is normal while the application is shutting down")
            return

        # Get the plugin's object
        plugin = self.plugins.get(plugin_name)
        if plugin is None:
            # Ensure what we recived was actually valid
            return

        # Try to get the function
        try:
            function = plugin.__getattribute__(function_name)
            # We succeed here
        except AttributeError as e:
            # That attribute doesn't exist
            print(f"[PLUGIN MANAGER | ERROR] Error calling into plugin: {plugin_name}.{function_name} {args}. Exception: {e}")
            return

        # Make sure that it's actually a function that we can call
        if not isinstance(function, types.MethodType):
            # If it's not, print an error and return
            print(f"[PLUGIN MANAGER | ERROR] Error calling into plugin: {plugin_name}.{function_name} {args}. Attribute is not of MethodType")
            return
        
        # Get the number of threads, warn the user if there are too many
        num_threads = len(self.executor._threads)
        if num_threads == self.max_workers:
            print(f"[PLUGIN MANAGER | WARN] There are too many threads running ({num_threads}/{self.max_workers})! Tasks will be queued, events may arrive to plugins late! You should adjust max_threads")
        
        # Get the plugin's blame, if it's blame is too high we execuete this
        if self.plugin_blame[plugin_name] >= self.max_blame:

            # Discard the event and never send it to the plugin
            if self.blame_action == "discard":
                print(f"[PLUGIN MANAGER | WARN] Plugin {plugin_name}'s blame is too high! Discarding event")
                return

        # We're ready to submit a task after... A lot of checks.
        future = self.executor.submit(function, args)
        future.add_done_callback(lambda future: self.plugin_done_function(future, plugin_name))
        print(f"[PLUGIN MANAGER | DEBUG] There are now {num_threads} running out of {self.max_workers}")  # A little bit of debug

        # Add one to the blame
        self.plugin_blame[plugin_name] += 1
        print(f"[PLUGIN MANAGER | DEBUG] {plugin_name}'s blame is {self.plugin_blame[plugin_name]} (max {self.max_blame})")  # Debugging

    def load_plugin(self, filename):
        plugin_name = filename[:-3]  # Remove ".py" extension
        json_path = f"{plugin_name}.json"  # Find the coresponding JSON
        plugin_path = os.path.join(self.plugin_dir, filename)
        
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        # Look at only the first member found
        members =  inspect.getmembers(plugin_module)
        self.plugin_blame[plugin_name] = 0
        for name, obj in members:
            if self.is_plugin_valid(obj):
                try:
                    o = obj()
                    o.__name__ = plugin_name
                    o.__file__ = plugin_path
                    o.__json__ = json_path
                    o.__signal__ = self.gui_signal
                    self.plugins[plugin_name] = o
                    print(f"[PLUGIN MANAGER | INFO] LOAD PLUGIN {plugin_name}: Calling into event_load")

                    self.plugin_run_function(plugin_name, "event_load")

                    print(f"[PLUGIN MANAGER | INFO] LOAD PLUGIN {plugin_name}: the call went through!")
                except Exception as e:
                    # Just skip loading it if the plugin errors
                    print(f"[PLUGIN MANAGER | ERROR] Error loading plugin {plugin_name}, unhandled exception: {e}")
                    self.gui_signal.emit(f"[PLUGIN MANAGER | ERROR] Error loading plugin {plugin_name}, caught exception: {e}")
                    continue

    def configure_plugin(self, plugin):
        name = plugin.__name__
        file = os.path.join(self.plugin_dir, plugin.__json__)
        with open(file, "r") as f:
            print(f"[PLUGIN MANAGER | INFO] Configuring {name}: {file}")
            data = json.load(f)
            self.plugin_run_function(name, "configure", (data,))

    def configure_plugins(self):
        for name, plugin in self.plugins.items():
            self.configure_plugin(plugin)
            self.gui_signal.emit(f"[PLUGIN MANAGER | INFO] Configured plugin {name}")

    def unload_plugins(self):
        for name, plugin in self.plugins.items():
            self.gui_signal.emit(f"[PLUGIN MANAGER | INFO] Shutting down plugin {name}")
            try:
                # Not submitting the task here, it's important this is syncronous.
                plugin.event_kill()
            except Exception as e:
                self.gui_signal.emit(f"[PLUGIN MANAGER | INFO] While shutting down plugin {name}: event_kill method caused an exception ({e}); Skipping shutdown")

        self.executor.shutdown()
        self.gui_signal.emit(f"[PLUGIN MANAGER | INFO] Shut down ThreadPoolExecutor of {self.max_workers} threads")

    def notify(self, source:str | None, dest:str, data:str):
        self.plugins[dest].event_notify(source, data)
