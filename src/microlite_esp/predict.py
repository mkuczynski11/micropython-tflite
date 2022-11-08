from model import ModelManager
from app_manager import AppManager
from app import app

import uasyncio as asyncio

# Import and initialize template loader
import utemplate.source
template_loader = utemplate.source.Loader(None, "templates")

async def main_loop():
    model_manager = ModelManager()
    app_manager = AppManager()
    msg_count = 0
    while True:
        # If else for message type from other board
        if msg_count == 0:
            # Mock of ssid and password values
            ssid = "UPC240648036"
            # Mock of ssid and password values
            password = "6SSGYAWT"
            ifconfig = app_manager.init_wifi_connection(ssid, password)
            print(f'Connection configuration:{ifconfig}')
        
        msg_count += 1
        await asyncio.sleep(1)

# Compile web service templates
for template in uos.listdir("templates"):
    if template.rsplit('.')[1] == "tpl":
        template_loader.load(template)

# Create async task for communication handling and predict operations
asyncio.create_task(main_loop())
# Run web service app
app.run(host="0.0.0.0", port = 80)
