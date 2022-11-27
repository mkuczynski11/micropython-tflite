from utils import singleton, get_file_size, get_free_space
import espnow
import aioespnow
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
 
    def __init__(self, peer_mac, sta_if, is_async=False):
        self._peer_mac = peer_mac
        self._sta_if = sta_if
       
        if is_async:
            self._espnow = aioespnow.AIOESPNow()
        else:
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
       
    def receive_message(self, timeout=0):
        _, msg = self._espnow.recv(timeout)
           
        message_type = None
        for key, value in ESPNowMessages.RESP.items():
            if msg == value:
                message_type = key
                break
       
        return message_type
 
    def send_prediction_request(self, file_path):
        file_size = get_file_size(file_path)
        print(file_size)
 
        success = self._espnow.send(self._peer_mac, ESPNowMessages.REQ["PREDICT"])
        success = success and self._espnow.send(self._peer_mac, f'{file_size}')
 
        current_chunk = 0
        i = 0
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(self.MAX_CHUNK_SIZE)
                current_chunk += 1
 
                if not chunk:
                    break
 
                time.sleep(0.1)
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
   
    async def areceive_message(self):
        _, msg = await self._espnow.arecv()
 
        message_type = None
        for key, value in ESPNowMessages.REQ.items():
            if msg == value:
                message_type = key
                break
       
        return message_type
   
    async def asend_message(self, message_type):
        print(f'Sending {message_type}')
        message = ESPNowMessages.RESP[message_type]
        print(f'Translated to {message}')
        received = await self._espnow.asend(self._peer_mac, message)
 
        return received
 
    async def asend_text(self, text):
        received = await self._espnow.asend(self._peer_mac, text)
 
        return received
   
    async def arecieve_model(self):
        _, model = await self._espnow.arecv()
       
        model_str = model.decode('utf-8')
        return model_str
   
    async def arecieve_wifi_details(self):
        _, wifi_details = await self._espnow.arecv()
       
        wifi_details = wifi_details.decode('utf-8').split('&')
        return (wifi_details[0], wifi_details[1])
 
    async def areceive_file(self):
 
        _, file_size_bytes = await self._espnow.arecv()
        file_size = int(file_size_bytes.decode('utf-8'))
        print(f'File with size {file_size} incoming!')
       
        if file_size > get_free_space(MICROSD_DIRECTORY):
            return False
 
        chunks_amount = 0
 
        if file_size % self.MAX_CHUNK_SIZE == 0:
            chunks_amount = int(file_size) // int(self.MAX_CHUNK_SIZE)
        else:
            chunks_amount = int(file_size) // int(self.MAX_CHUNK_SIZE) + 1
 
        with open(TMP_IMAGE_PATH, "wb") as f:
            print(f'chunks {chunks_amount}')
            for i in range(chunks_amount):
                _, chunk = await self._espnow.arecv()
                print(f'{i}:{chunk}')
                file_size -= self.MAX_CHUNK_SIZE
 
                f.write(chunk)
 
        print('File received!')
        return True
    
