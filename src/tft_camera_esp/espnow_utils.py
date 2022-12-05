from utils import singleton, get_file_size, get_free_space
import espnow
import time
from config import MICROSD_DIRECTORY, TMP_IMAGE_PATH
 
class ESPNowMessages:
    REQ = {
        "PREDICT": b"<PREDICT_REQ>",
        "WIFI_CONNECT": b"<WIFI_CONNECT_REQ>",
        "GET_MODELS": b"<GET_MODELS_REQ>",
        "CHANGE_MODEL": b"<CHANGE_MODEL_REQ>"
    }
 
    RESP = {
        "WIFI_CONNECT_FAIL": b"<WIFI_CONNECT_FAIL_RESP>",
        "WIFI_CONNECT_SUCCESS": b"<WIFI_CONNECT_SUCCESS_RESP>",
        "CHANGE_MODEL_SUCCESS": b"<CHANGE_MODEL_SUCCESS_RESP>",
        "CHANGE_MODEL_FAIL": b"<CHANGE_MODEL_FAIL_RESP>",
        "PREDICT_FAIL" : b"<PREDICT_FAIL_RESP>",
        "PREDICT_SUCCESS" : b"<PREDICT_SUCCESS_RESP>"
    }
 
 
@singleton
class ESPNowCommunicationManager:
 
    MAX_CHUNK_SIZE = 250
 
    def __init__(self, peer_mac, sta_if):
        self._peer_mac = peer_mac
        self._sta_if = sta_if
       

        self._espnow = espnow.ESPNow()
        self._espnow.active(True)
        self._espnow.add_peer(self._peer_mac)
 
        if not sta_if.active():
            sta_if.active(True)
 
    def send_message(self, message_type):
        message = ESPNowMessages.REQ[message_type]
        received = self._espnow.send(self._peer_mac, message)
 
        return received
   
    def send_wifi_credentials(self, ssid, password):
        message = f'{ssid}&{password}'
        received = self._espnow.send(self._peer_mac, message)
       
        return received
   
    def send_model_name(self, model_name):
        received = self._espnow.send(self._peer_mac, model_name)
       
        return received
   
    def receive_text(self):
        _, text_bytes = self._espnow.recv()
       
        message = text_bytes.decode('utf-8')
        return message
       
    def receive_message(self):
        _, msg = self._espnow.recv()
           
        message_type = None
        for key, value in ESPNowMessages.RESP.items():
            if msg == value:
                message_type = key
                break
       
        return message_type
 
    def send_prediction_request(self, file_path, sta, ap):

        file_size = get_file_size(file_path)
 
        self._espnow.send(self._peer_mac, ESPNowMessages.REQ["PREDICT"])

        if not sta.isconnected():
            sta.active(False)
            ap.active(False)
            sta.active(True)
            ap.active(True)
            sta.config(channel=1, reconnects=0)
            while not sta.active():
                time.sleep(0.1)
            sta.disconnect()
            while sta.isconnected():
                time.sleep(0.1)
    
        self._espnow.send(self._peer_mac, f'{file_size}')
        
        current_chunk = 0
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(self.MAX_CHUNK_SIZE)
                current_chunk += 1
 
                if not chunk:
                    break
 
                time.sleep(0.2)
                self._espnow.send(self._peer_mac, chunk, False)
       
    def receive_models(self):
        """
           Returns tuple containing list of available models and active model
       """
        _, models_bytes = self._espnow.recv()
       
        models_str = models_bytes.decode('utf-8')
        models = models_str.split('&') # DODAJ DO CONFIGa
       
        active_model = self.receive_text()
       
        return (models, active_model)
   
    def receive_prediction(self):
        _, prediction = self._espnow.recv()
       
        prediction_str = prediction.decode('utf-8')
        return prediction_str