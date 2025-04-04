'''
Module containing plugin interfaces and definitions, does not contain any plugins
'''

from abc import ABC, abstractmethod

class PluginInterface(ABC):
    '''
    # Fake Variables
    When set up by PluginManager, "dunder" variables (some standard, some custom) are set
    to allow the plugin to know its properties. Below is a list of these variables

    - __name__
        Holds the true name of the plugin, this is it's filename without the extension
        For example, a plugin named `tts.py` becomes `tts`
    
    - __file__
        Holds the canonical path of the main python file
    
    - __json__
        Holds the canonical path to the corresponding JSON file
    '''
    @abstractmethod
    def event_load(self, logger):
        '''
        This method must be implemented by all plugins.
        This method will be called to initalize the plugin's behaviour
        '''
        pass

    @abstractmethod
    def event_kill(self):
        '''
        This method must be implemented by all plugins.
        This method will be called when the application exits
        '''
        pass

    @abstractmethod
    def event_message(self, message):
        '''
        This method must be implemented by all plugins.
        This method will be called when a message is recived
        '''
        pass

    @abstractmethod
    def event_notify(self, source, data):
        '''
        Plugins may send data to others by this method.
        It will be called when a notification happens

        TODO: The method to send data isn't implemented
        '''
        pass
    
    @abstractmethod
    def event_main(self, t, loop_wait):
        '''
        This is called every time chat messages are polled

        `t` is `time.time_ns()`, time in nanoseconds since the UINX epoch
        `loop_wait` is `config["Backend"]["loop_wait_ns"]`, time in nanoseconds that each wait takes
        '''
        pass

    @abstractmethod
    def configure(self, config:dict):
        '''
        This method must be implemented by all plugins.
        This method will be called to configure the plugins behaviour
        '''
        pass
