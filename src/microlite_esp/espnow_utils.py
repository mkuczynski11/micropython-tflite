from utils import singleton, get_file_size, get_free_space
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
 
    def __init__(self, peer_mac, sta_if):
        self._peer_mac = peer_mac
        self._sta_if = sta_if
        self._espnow = aioespnow.AIOESPNow()
        self._espnow.active(True)
        self._espnow.add_peer(self._peer_mac)
 
        if not sta_if.active():
            sta_if.active(True)
   
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
       
        result = True
        if file_size > get_free_space(MICROSD_DIRECTORY):
            result = False
         
        chunks_amount = 0
 
        if file_size % self.MAX_CHUNK_SIZE == 0:
            chunks_amount = int(file_size) // int(self.MAX_CHUNK_SIZE)
        else:
            chunks_amount = int(file_size) // int(self.MAX_CHUNK_SIZE) + 1
 
        with open(TMP_IMAGE_PATH, "wb") as f:
            for i in range(chunks_amount):
                _, chunk = await self._espnow.arecv()
                file_size -= self.MAX_CHUNK_SIZE
 
                if result:
                    f.write(chunk)
 
        print('File received!')
        return result
    
