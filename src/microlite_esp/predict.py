from model import ModelManager
from app_manager import AppManager
from app import app

import uasyncio as asyncio

async def main_loop():
    print("Starting main loop")
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
            app_manager.init_wifi_connection(ssid, password)          
        
        msg_count += 1
        await asyncio.sleep(1)
        
        
    print("Ending main loop")
    
asyncio.create_task(main_loop())
# Check IP of the device for connection
app.run(host="0.0.0.0", port = 80)
