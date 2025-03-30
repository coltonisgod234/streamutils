import os
import concurrent.futures as cf
import importlib.util
import inspect
import pluginsdk
import json
import logging
import types

class PluginManager:
    '''
    Class to manage plugins
    '''
    def __init__(self, plugin_dir, base_dir=os.path.abspath(__file__), signal=None, config=None, logger=None):
        # Directory the program is installed in
        self.install_dir = base_dir  

        # Directory to load plugins from
        self.plugin_dir = plugin_dir

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
        self.blame_queues = {}

        # Execute plugins in paralel
        self.executor = cf.ThreadPoolExecutor(max_workers=self.max_workers)

        self.logger = logger

        self.logger.info(f"Plugin directory path is: {plugin_dir}")
        self.logger.info(f"concurent.futures has spawned a {self.use_threads}-based executor with {self.max_workers} workers.")

    def is_plugin_enabled(self, plugin_name):
        '''
        Returns True is a plugin is enabled in the config and False if it is not
        '''
        return self.config["Plugins.enable"].getboolean(plugin_name)
    
    def is_file_plugin(self, filename):
        '''
        Returns True if a given filename is a plugin and False otherwise
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
        self.logger.info("START: Loading plugins...")
        if not os.path.exists(self.plugin_dir):
            self.logger.error("END: Plugin directory path does not exist?")
            return
        
        if not os.path.isdir(self.plugin_dir):
            self.logger.error("END: Plugin directory path is not a directory?")
            return
        
        # Loop through all the plugins
        plugin_dirs = []
        for directory in os.listdir(self.plugin_dir):
            path = os.path.join(self.plugin_dir, directory)
            self.logger.info(f"Searching for dirs... {directory}, {path}")

            if path.find("__pycache__") == -1:
                plugin_dirs.append(path)
        
        self.logger.info(f"Directories to search: {plugin_dirs}")
        for path in plugin_dirs:
            if path.find("__pycache__") != -1:
                self.logger.info(f"Skipping {path}...")
                continue

            self.logger.info(f"Scanning {path}...")
            self.load_plugin(path)
            self.logger.info(f"{path} is loaded")

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
        self.logger.debug(f"END: Call to plugin {name} complete (future {future}, {id(future)})")
        self.plugin_blame[name] -= 1
        self.logger.debug(f"{name}'s blame is {self.plugin_blame[name]} (max {self.max_blame})")
    
    def plugin_run_function(self, plugin_name:str, function_name:str, args:tuple=()):
        '''
        Run a given function from a plugin
        '''
        self.logger.debug(f"START: Calling plugin function call: {plugin_name}.{function_name} {args}...")
        # Ensure the executor is still alive and hasn't terminated
        if self.executor._shutdown:
            self.logger.error(f"END: Attempted to start a new task on {self.use_threads}-based executor after it's shutdown! Ignoring request.")
            self.logger.info("^^^ The above error is normal while the application is shutting down")
            return

        # Get the plugin's object
        plugin = self.plugins.get(plugin_name)
        if plugin is None:
            # Ensure what we recived was actually valid
            self.logger.error(f"END: Error calling into plugin: {plugin_name}.{function_name} {args}. `{plugin_name}` is not in `plugins` ({e})")
            return

        # Try to get the function
        try:
            function = plugin.__getattribute__(function_name)
            # We succeed here
        except AttributeError as e:
            # That attribute doesn't exist
            self.logger.error(f"END: Error calling into plugin: {plugin_name}.{function_name} {args}. Can't retrive function `{function_name}` ({e})")
            return

        # Make sure that it's actually a function that we can call
        if not isinstance(function, types.MethodType):
            # If it's not, print an error and return
            self.logger.error(f"END: Error calling into plugin: {plugin_name}.{function_name} {args}. Attribute is not of `MethodType`")
            return
        
        # Get the number of threads, warn the user if there are too many
        num_threads = len(self.executor._threads)
        if num_threads == self.max_workers:
            self.logger.warning(f"There are too many threads running ({num_threads}/{self.max_workers})! Tasks will be queued.")
        
        # Get the plugin's blame, if it's blame is too high we execuete this
        if self.plugin_blame[plugin_name] >= self.max_blame:

            # Discard the event and never send it to the plugin
            if self.blame_action == "discard":
                self.logger.warning(f"Plugin `{plugin_name}`: blame is too high! Discarding event")
                return
            
            if self.blame_action == "buffer":
                self.blame_queues[plugin_name].append([function_name, args])
                self.logger.debug(f"Plugin `{plugin_name}`: blame is too high! Buffer... {self.blame_queues[plugin_name]}")
                if len(self.blame_queues[plugin_name]) >= 1:
                    nxt = self.blame_queues[plugin_name].pop()
                    future = self.executor.submit(nxt[0], nxt[1])
                    self.logger.debug(f"Executing {nxt} from buffer {self.blame_queues[plugin_name]}.")

        # We're ready to submit a task after... A lot of checks.
        future = self.executor.submit(function, args)
        future.add_done_callback(lambda future: self.plugin_done_function(future, plugin_name))

        self.logger.debug(f"There are now {num_threads} running out of {self.max_workers}")  # A little bit of debug

        # Add one to the blame
        self.plugin_blame[plugin_name] += 1
        self.logger.debug(f"{plugin_name}'s blame is {self.plugin_blame[plugin_name]} (max {self.max_blame})")  # Debugging

    def load_plugin(self, path, filename=None, config=None):
        '''
        Load a given plugin from a filename
        '''
        self.logger.info(f"START: Load {filename}")

        if filename is None:
            filename = "main.py"

        if config is None:
            json_path = os.path.join(path, "config.json")

        plugin_path = os.path.join(path, filename)
        plugin_name = plugin_path

        self.logger.info(f"path={plugin_path}, name={plugin_name}, json={json_path}")
        
        # Load the plugin's spec from the path
        self.logger.info(f"Generating and loading spec for {filename}...")
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)

        # Create a module from that spec
        plugin_module = importlib.util.module_from_spec(spec)

        # Load that module to create it's attributes
        self.logger.info(f"Executing module {filename}...")
        spec.loader.exec_module(plugin_module)
        
        # Look at only the first member found
        members =  inspect.getmembers(plugin_module)

        # Initalize it's blame to 0
        self.plugin_blame[plugin_name] = 1
        self.blame_queues[plugin_name] = []

        for name, obj in members:
            if self.is_plugin_valid(obj):
                try:
                    o = obj()

                    # Create some special variables to hold info about this plugin
                    o.__name__ = plugin_name
                    o.__file__ = plugin_path
                    o.__json__ = json_path
                    o.__signal__ = self.gui_signal
                    self.logger.info(f"Loaded plugin name={o.__name__} file={o.__file__} json={o.__json__}")

                    # Add it to the plugins
                    self.plugins[plugin_name] = o
                    self.logger.info(f"{plugin_name}: Calling into event_load")

                    # Run it's load function
                    logger = logging.getLogger(f"plugins.{plugin_name}")
                    self.plugin_run_function(plugin_name, "event_load", (logger))
                except Exception as e:
                    # Just skip loading it if the plugin errors
                    self.logger.error(f"Error loading plugin {plugin_name}, caught exception: {e}")
                    self.gui_signal.emit(f"Error loading plugin {plugin_name}, caught exception: {e}")  # Notify the user
                    continue

    def configure_plugin(self, plugin):
        '''
        Configure a plugin by calling it's `configure` function
        '''
        name = plugin.__name__  # Get the plugin's name

        # Find the corresponding JSON file
        file = plugin.__json__

        # Open the JSON and read the data
        with open(file, "r") as f:
            self.logger.info(f"Configuring {name}: {file}")
            data = json.load(f)

            # Call its configure function
            self.plugin_run_function(name, "configure", (data,))

    def configure_plugins(self):
        '''
        Configure every plugin that has been loaded
        '''

        # Loop through all the loaded plugin
        for name, plugin in self.plugins.items():
            self.configure_plugin(plugin)  # Configure it

            # Notify the user
            self.gui_signal.emit(f"Configured plugin {name}")

    def unload_plugins(self):
        '''
        Unload all the plugins and shut them down
        '''

        # Loop through all the plugins
        self.logger.info("Shutting down all plugins... THIS CAN TAKE A LONG TIME!")
        for name, plugin in self.plugins.items():
            self.logger.info(f"Shutting down plugin {name}...")
            try:
                # Not submitting the task here, it's important this is syncronous.
                plugin.event_kill()
                self.logger.info(f"Shut down plugin {name} successfully")
            except Exception as e:
                self.logger.error(f"While shutting down plugin {name}: event_kill method caused an exception ({e}); Skipping shutdown")

        self.executor.shutdown()
        self.logger.info(f"Shut down executor of {self.max_workers} threads")

    def notify(self, source:str | None, dest:str, data:str):
        '''
        TODO
        '''
        self.plugins[dest].event_notify(source, data)
