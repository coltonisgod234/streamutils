class PluginExample:
    def nullevent(self):
        #print(f"{time_ns()} Doing stuff")
        pass

    def startup(self, config):
        print(f"Startup")
    
    def destroy(self):
        print(f"Shutdown")
    
    def message(self, message):
        print("Plugin got message", message.stringified)