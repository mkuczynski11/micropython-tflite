import utime
import network
import ntptime
import uos

from utils import singleton
from config import TMP_MODEL_PATH

@singleton
class AppManager:
    def __init__(self):
        self.ssid = ""
        self.password = ""
        self.model_passed = False
        self.labels_passed = False

    def init_wifi_connection(self, ssid, password):
        sta_if = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.password = password
        start = utime.time()
        timed_out = False
        
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected() and not timed_out:
                if utime.time() - start >= 20:
                    timed_out = True
                else:
                    pass
        
        if sta_if.isconnected():
            print('network config:', sta_if.ifconfig())
        else: 
            print('internet not available')
            
    def reset_model_creation(self):
        self.model_passed = False
        self.labels_passed = False
        self.clear_tmp_resources()
        
    def clear_tmp_resources(self):
        for file in uos.listdir(TMP_MODEL_PATH):
            uos.remove(TMP_MODEL_PATH + '/' + file)
        
    def is_able_to_create_model(self):
        return self.model_passed and self.labels_passed
    