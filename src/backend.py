USE_PYTCHAT = True
USE_IRC = True
PYTCHAT_URL = "https://www.youtube.com/watch?v=jfKfPfyJRdk"

import pytchat
import plugins
import asyncio

async def main():
    manager = plugins.PluginManager()
    await manager.load_plugin_from_path("example", "plugins/test.py", {})

    chat = pytchat.create(video_id=PYTCHAT_URL)
    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"{c.author.name}: {c.message}")
            await manager.msg_all(c)

asyncio.run(main())