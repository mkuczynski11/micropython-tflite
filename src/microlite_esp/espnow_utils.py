from utils import singleton, get_file_size
from config import TMP_IMAGE_PATH
import espnow
import aioespnow

class ESPNowMessages:
    REQ = {
        "PREDICT": b"<PREDICT_REQ>",
        "WIFI_CONNECT": b"<WIFI_CONNECT_REQ>",
        "GET_MODELS": b"<GET_MODELS_REQ>",
        "CHANGE_MODEL": b"<CHANGE_MODEL_REQ>"
    }

    RESP = {
        "PREDICT": b"<PREDICT_RESP>",
        "WIFI_CONNECT_SUCCESS": b"<WIFI_CONNECT_SUCCESS_RESP>",
        "WIFI_CONNECT_FAIL": b"<WIFI_CONNECT_FAIL_RESP>",
        "CHANGE_MODEL_SUCCESS": b"<CHANGE_MODEL_SUCCESS_RESP>",
        "CHANGE_MODEL_FAIL": b"<CHANGE_MODEL_FAIL_RESP>"
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

    async def receive_message(self):
        _, msg = await self._espnow.arecv()

        message_type = None
        for key, value in ESPNowMessages.REQ.items():
            if msg == value:
                message_type = key
                break
        
        return message_type
    
    async def send_message(self, message_type):
        print(f'Sending {message_type}')
        message = ESPNowMessages.RESP[message_type]
        print(f'Translated to {message}')
        received = await self._espnow.asend(self._peer_mac, message)

        return received

    async def send_file(self, file_path):
        file_size = get_file_size(file_path)

        await self._espnow.asend(self._peer_mac, ESPNowMessages.REQ["PREDICT"])
        await self._espnow.asend(self._peer_mac, f'{file_size}')

        current_chunk = 0

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(self.MAX_CHUNK_SIZE)
                current_chunk += 1

                if not chunk:
                    break

                await self._espnow.asend(self._peer_mac, chunk)

    async def send_models(self, models):
        received = await self._espnow.asend(self._peer_mac, models)

        return received
    
    async def send_prediction(self, class_name):
        recieved = await self._espnow.asend(self._peer_mac, class_name)
        
        return recieved

    async def receive_models(self):
        _, models_bytes = await self._espnow.arecv()
        
        models_str = models.decode('utf-8')
        models = models_str.split('&') # DODAJ DO CONFIGa
        return models
    
    async def recieve_model(self):
        _, model = await self._espnow.arecv()
        
        model_str = model.decode('utf-8')
        return model_str
    
    async def recieve_wifi_details(self):
        _, wifi_details = await self._espnow.arecv()
        
        wifi_details = wifi_details.decode('utf-8').split('&') # DODAJ DO CONFIG
        return (wifi_details[0], wifi_details[1])

    async def receive_file(self):

        _, file_size_bytes = await self._espnow.arecv()
        file_size = int(file_size_bytes.decode('utf-8'))
        print(f'File with size {file_size} incoming!')

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

                # Obsolete I believe
                # if file_size < self.MAX_CHUNK_SIZE:
                #     chunk = chunk[:file_size]
                f.write(chunk)

        print('File received!')
