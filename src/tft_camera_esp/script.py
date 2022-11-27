import camera
from machine import Pin, SPI
import st7789
import network
from espnow_utils import ESPNowCommunicationManager
import time
import utime
from ap_service import CredentialsService

SSID = "GalaxyNote1005a8"
PASSWORD = "zcyj6141"

PREDICT_BUTTON = Pin(22, Pin.IN, Pin.PULL_UP) # YELLOW  | predict
MODEL_BUTTON = Pin(21, Pin.IN, Pin.PULL_UP) # MIDDLE RED | open model menu / choose 
AP_BUTTON = Pin(19, Pin.IN, Pin.PULL_UP) # LAST RED openAP / scroll down

mosi = 13
sck = 14
cs = 15
dc = 2
rst = 12
baud = 31250000

MARKER_SIZE = (16, 16)
PER_PAGE = 12 # There can be only 15 positions in the list to display
GO_BACK_PROMPT = '> Go back'


def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=31250000, sck=Pin(sck), mosi=Pin(mosi)),
        240,
        240,
        reset=Pin(rst, Pin.OUT),
        cs=Pin(cs, Pin.OUT),
        dc=Pin(dc, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)

def connect_wifi(espnow_manager, ssid, password, sta, ap):
    espnow_manager.send_message("WIFI_CONNECT")
    espnow_manager.send_wifi_credentials(ssid, password)
#     sta.config(channel=1) # TODO: Setup common channel after activating wifi interface
    
#     nets = sta.scan()
#     channel = 1
#     for net in nets:
#         print(net)
#         if net[0].decode('utf-8') == SSID:
#             print(f'Network channel = {net[2]}')
#             channel = net[2]
#             break
#     time.sleep(5) # TODO CHANGEEEE

    start = utime.time()
    timed_out = False
        
    if not sta.isconnected():
        sta.active(True)
        sta.connect(SSID, PASSWORD)
        while not sta.isconnected() and not timed_out:
            if utime.time() - start >= 20:
                timed_out = True
            else:
                pass
        
    if sta.isconnected():
        ap.active(True)
        print(f'Active channel is {sta.config("channel")}')
        config = sta.ifconfig()

#     sta.config(channel=channel)
#     sta.active(True)
    
    message = espnow_manager.receive_message()
    ip = None
    
    if message == "WIFI_CONNECT_SUCCESS":
        ip = espnow_manager.receive_text()
    
    return (message, ip)

    
def change_model(espnow_manager, model_name):
    espnow_manager.send_message("CHANGE_MODEL")
    espnow_manager.send_model_name(model_name)
    
    message = espnow_manager.receive_message()
    
    if message == "CHANGE_MODEL_FAIL":
        message = espnow_manager.receive_text()
    
    return message
    
def predict(espnow_manager, camera, file_name):
    buf = camera.capture()
        
    espnow_manager.send_prediction_request(file_name)

    message = espnow_manager.receive_message()
    error_message = None
    print(f'msg == {message}')
        
    if message == "PREDICT_FAIL":
        error_message = espnow_manager.receive_text()
        
        return ('PREDICTION_FAIL', error_message)
    elif message == "PREDICT_SUCCESS":
        message = espnow_manager.receive_text()
        resp_arr = message.split('&')
        predicted_class = resp_arr[0]
        prediction_result = resp_arr[1]
        
        return (predicted_class, prediction_result)


def get_wifi_credentials(ap_if):
    service = CredentialsService("BetterDontAsk", "12345678", ap_if)
    
    service.start_ap()
    ssid, password = service.wait_for_credentials()
    print(f'Received ssid = {ssid}, password = {password}')


def main():
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
    camera.framesize(camera.FRAME_240X240)
    
    buf = camera.capture()
    
    with open('img.jpg', 'wb') as f:
        f.write(buf)

    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    sta.active(True)
    sta.config(channel=1, reconnects=0)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()
    while sta.isconnected():
        time.sleep(0.1)
    
#     get_wifi_credentials(ap)

    peer = b'\xec\x62\x60\x9d\x03\xec'
    
    espnow_manager = ESPNowCommunicationManager(peer, sta)
    
    print('Sent request to connect to wifi')
    message = connect_wifi(espnow_manager, SSID, PASSWORD, sta, ap)
    print(f'Response from connect_wifi = {message}')
 
    
    print('Sent request to get models')
    espnow_manager.send_message("GET_MODELS")
    models = espnow_manager.receive_models()
    print(models)
           
    print('Sent request to change model')
    message = change_model(espnow_manager, 'garbage')
    print(message)
    
#   print('Sent request to predict')
    
    message = predict(espnow_manager, camera, 'img.jpg')
    print(message)
    time.sleep(10)
    peeee = espnow_manager._espnow.get_peer(peer)
    print(peeee)
    
    message = predict(espnow_manager, camera, 'img.jpg')
    print(message)
    message = predict(espnow_manager, camera, 'img.jpg')
    print(message)

    
#     print('Sent request to connect to wifi')
#     message = connect_wifi(espnow_manager, SSID, PASSWORD, sta)
#     print(f'Response from connect_wifi = {message}')
# 
# #     print('Sent request to predict')
# #     message = predict(espnow_manager, camera, 'img.jpg')
# #     print(message)
# #     
# #         
# #         tft.jpg_from_buffer(buf, 0, 0)

    # Camera & display code
    tft = config(0)
    tft.init()
    tft.fill(st7789.BLACK)
    
#     while True:
#         if not PREDICT_BUTTON.value():
#             print('Prediction!!!')
#             time.sleep(0.5)
#             
#         if not MODEL_BUTTON.value():
#             print('Model menu!!!')
#             time.sleep(0.5)
# 
#         if not AP_BUTTON.value():
#             print('Access point!!!')
#             time.sleep(0.5)
        
        
    camera.deinit()

main()

