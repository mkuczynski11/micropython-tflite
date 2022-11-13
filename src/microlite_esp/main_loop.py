from model import ModelManager
from app_manager import AppManager
from espnow_utils import ESPNowCommunicationManager
from app import app

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
        msg_type = await esp_manager.receive_message()

        if msg_type == "PREDICT":
            await esp_manager.receive_file()
            
            if model_manager.active_model_name == None:
                await esp_manager.send_prediction("Model not loaded")
                continue
            
            class_name = model_manager.model_executor.predict(model_manager.current_image_path)
        
            await esp_manager.send_prediction(class_name)
            
            model_name = model_manager.model_executor.config.name
            classified_count = len(uos.listdir(model_manager.images_path + '/' + model_name + '/' + class_name))
            uos.rename(model_manager.current_image_path, model_manager.images_path + '/' + model_name + '/' + class_name + '/' + class_name + str(classified_count + 1) + '.jpg')
        elif msg_type == "WIFI_CONNECT":
            ssid, password = await esp_manager.recieve_wifi_details()
            result = app_manager.init_wifi_connection(ssid, password)
            if result:
                await esp_manager.send_message("WIFI_CONNECT_SUCCESS")
            else:
                await esp_manager.send_message("WIFI_CONNECT_FAIL")
        elif msg_type == "GET_MODELS":
            model_list = app_manager.get_model_list()
            model_list_string = '&'.join(model_list)
            await esp_manager.send_models(model_list_string)
        elif msg_type == "CHANGE_MODEL":
            model = await esp_manager.recieve_model()
            ok = model_manager.load_model(model)
            if ok:
                await esp_manager.send_message("CHANGE_MODEL_SUCCESS")
            else:
                await esp_manager.send_message("CHANGE_MODEL_FAIL")

# Compile web service templates
for template in uos.listdir("templates"):
    if template.rsplit('.')[1] == "tpl":
        template_loader.load(template)

# Create async task for communication handling and predict operations
asyncio.create_task(main_loop())
# Run web service app
app.run(host="0.0.0.0", port = 80)

