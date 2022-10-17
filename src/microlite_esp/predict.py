from config import config
from model import ModelConfig, Model, ModelExecutor, ModelManager
from app_manager import AppManager
from app import app

import uasyncio as asyncio

async def main_loop():
    print("Starting main loop")
    model_manager = ModelManager()
    app_manager = AppManager(model_manager)
    
    # TODO: This should be created when user picks the model
    model_config = ModelConfig(config)
    model = Model(model_config.size, model_config.input_size)
    model.read_model(model_config.path)
    model_executor = ModelExecutor(model, model_config)
    model_executor.init_interpreter()
    
    model_manager.reload_model(model_executor)
    
    msg_count = 0
    while True:
        # If else for message type from other board
        if msg_count == 0:
            # Mock of ssid and password values
            ssid = "UPC240648036"
            # Mock of ssid and password values
            password = "6SSGYAWT"
            app_manager.init_wifi_connection(ssid, password)
        else:
            model_manager.predict_scenario()
        
        msg_count += 1
        await asyncio.sleep(20)
        
    print("Ending main loop")
    
asyncio.create_task(main_loop())
# Check IP of the device for connection
app.run(host="0.0.0.0", port = 80)
