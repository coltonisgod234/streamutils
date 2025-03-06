import asyncio
import importlib.util
import sys

class Example:
    def run(self, message_queue: asyncio.Queue, event_queue: asyncio.Queue, config: dict):
        '''
        This method runs in a thread upon the plugins startup.

        Arguments
        ---------
        message_queue:
            Any argument named `message_queue` will be given an asyncio.Queue object
            to send pytchat message objects to the client

        event_queue:
            Any argument named `event_queue` will be given an asyncio.Queue object
            to communicate with the host
        '''
        self.messages = message_queue
        self.events = event_queue
        self.config = config
        print("[Example] Plugin started!")

class PluginHost:
    def __init__(self, obj, config={}):
        self.object = obj
        self.message_queue = asyncio.Queue()
        self.event_queue = asyncio.Queue()
        self.config = config
        self.task:asyncio.Task = None
        print(f"PluginHost init but not started {self.object}")
    
    async def spawn(self):
        '''
        Spawn the asnycio '''
        print(f"Starting asyncio task {self.object}")
        self.task = asyncio.create_task(
            asyncio.to_thread(
                self.object.run,
                message_queue=self.message_queue,
                event_queue=self.event_queue,
                config=self.config
            )
        )
        print("PluginHost started asyncio task")
    
    async def message(self, data = None):
        await self.message_queue.put(data)
    
    async def event(self, type:str, data:dict = None):
        await self.event_queue.put({
            "type": type,
            "data": data
        })
    
    def stop(self):
        self.task.cancel()

class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    async def load_plugin_from_object(self, name, object, config):
        self.plugins[name] = PluginHost(
            obj=object,
            config=config
        )
        await self.plugins[name].spawn()
    
    async def load_plugin_from_path(self, name, path, config):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module

        spec.loader.exec_module(module)  # Execute it for some reason
        
        await self.load_plugin_from_object(name, module, config)
    
    def stop_plugin(self, name):
        p = self.plugins.get(name)
        if p == None:
            print(f"PluginManager can't stop unloaded plugin {name}")
            return
        
        p.stop()
        del p
        print(f"PluginManager stopped plugin")
    
    async def msg_all(self, c):
        print(self.plugins)
        for name, plugin in self.plugins.items():
            print(f"sending {name} message {c}")
            await plugin.message(c)

manager = PluginManager()
async def main():
    await manager.load_plugin_from_path("test", "plugins/test.py", {})
    manager.stop_plugin("test")

#asyncio.run(main())