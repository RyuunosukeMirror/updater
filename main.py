import asyncio
import app.updater

async def main():
    print(""" ______                                                   _             _ 
(_____ \                                                 | |           | |
 _____) ) _   _  _   _  _   _  ____    ___    ___  _   _ | |  _  _____ | |
|  __  / | | | || | | || | | ||  _ \  / _ \  /___)| | | || |_/ )| ___ ||_|
| |  \ \ | |_| || |_| || |_| || | | || |_| ||___ || |_| ||  _ ( | ____| _ 
|_|   |_| \__  ||____/ |____/ |_| |_| \___/ (___/ |____/ |_| \_)|_____)|_|
         (____/ > Updater v1.0.0 | Copyright (c) 2021- |
""")
    await app.updater.setup()
    await app.updater.run()

asyncio.run(main())


