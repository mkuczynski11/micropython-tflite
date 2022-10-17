import utime
import network
import ntptime

class AppManager:
    def __init__(self, model_manager):
        self.ssid = ""
        self.password = ""

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
            
        