from model import ModelManager
from app_manager import AppManager
from espnow_utils import ESPNowCommunicationManager
from app import app
from utils import ResponseCode
import time

import uasyncio as asyncio

# Import and initialize template loader
import utemplate.source
template_loader = utemplate.source.Loader(None, "templates")

async def main_loop():
    model_manager = ModelManager()
    app_manager = AppManager()
    esp_manager = ESPNowCommunicationManager(app_manager.get_peer_mac(), app_manager.get_network_interface())
    print('Starting to recieve messages')
    while True:
        msg_type = await esp_manager.areceive_message()
        
        if not app_manager.sta_if.isconnected(): # TODO: To function
            app_manager.wifi_reset()
            print(app_manager.sta_if.config("channel"))

        print(app_manager.sta_if.config("channel"))
        print(msg_type)
        if msg_type == "PREDICT":
            print("predict")
            
            ok = await esp_manager.areceive_file()
            if not ok:
                print("Not enough space on the device to save file")
                await esp_manager.asend_message("PREDICT_FAIL")
                await esp_manager.asend_text("no more space")
                continue
            
            if model_manager.active_model_name == None:
                await esp_manager.asend_message("PREDICT_FAIL")
                await esp_manager.asend_text("no model loaded")
                continue
            
            try:
                class_name, prediction = model_manager.model_executor.predict()
            except MemoryError as e:
                await esp_manager.asend_message("PREDICT_FAIL")
                await esp_manager.asend_text("device busy")
                continue
        
            await esp_manager.asend_message("PREDICT_SUCCESS")
            await esp_manager.asend_text(f'{class_name}&{prediction}')
                        
            model_name = model_manager.model_executor.config.name
            app_manager.move_image(model_name, class_name)
        elif msg_type == "WIFI_CONNECT":
            ssid, password = await esp_manager.arecieve_wifi_details()
            print("wifi")
            print(ssid)
            print(password)
            result = app_manager.init_wifi_connection(ssid, password)
            time.sleep(5)
            if result:
                await esp_manager.asend_message("WIFI_CONNECT_SUCCESS")
                await esp_manager.asend_text(result[0])
            else:
                await esp_manager.asend_message("WIFI_CONNECT_FAIL")
        elif msg_type == "GET_MODELS":
            print("get models")
            model_list = app_manager.get_model_list()
            model_list_string = '&'.join(model_list)
            await esp_manager.asend_text(model_list_string)
            active_model = "None"
            if model_manager.active_model_name is not None:
                print(f'There is active model = {model_manager.active_model_name}')
                active_model = model_manager.active_model_name
            await esp_manager.asend_text(active_model)
        elif msg_type == "CHANGE_MODEL":
            print("change models")
            model = await esp_manager.arecieve_model()
            code = model_manager.load_model(model)
            if code == ResponseCode.OK:
                await esp_manager.asend_message("CHANGE_MODEL_SUCCESS")
            else:
                await esp_manager.asend_message("CHANGE_MODEL_FAIL")
                await esp_manager.asend_text(code)

# Compile web service templates
for template in uos.listdir("templates"):
    if template.rsplit('.')[1] == "tpl":
        template_loader.load(template)

# Create async task for communication handling and predict operations
asyncio.create_task(main_loop())
# Run web service app
app.run(host="0.0.0.0", port = 80)
