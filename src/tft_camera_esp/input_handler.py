import camera
from machine import Pin, SPI
import st7789
import network
from espnow_utils import ESPNowCommunicationManager
import time
import utime
from ap_service import CredentialsService
import vga1_16x16 as font

SSID = "GalaxyNote1005a8"
PASSWORD = "zcyj6141"

AP_SSID = "MicroPython_AccessPoint"
AP_PASSWORD = "12345678"

# Set pins to correct ones
PREDICT_BUTTON = Pin(4, Pin.IN, Pin.PULL_UP) # YELLOW  | predict
MODEL_BUTTON = Pin(0, Pin.IN, Pin.PULL_UP) # MIDDLE RED | open model menu / choose 
AP_BUTTON = Pin(16, Pin.IN, Pin.PULL_UP) # LAST RED openAP / scroll down

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

def change_active_model(tft):
    """
    This method assumes that user have pressed button to enter model menu
    """
    def draw_page_counter(tft, page_number):
        """
        Displays page counter on the bottom of the page
        """
        tft.fill_rect(0, (PER_PAGE + 1) * 16, 240, 32, st7789.BLACK)
        tft.text(font, f'Page: {page_number}', 16, 16 * 14)

    tft.fill(st7789.BLACK)
        
    #models = [GO_BACK_PROMPT, '1garbage', '1vehicles', '1shrooms', '1garbage', '1vehicles', '1shrooms', '1garbage', '1vehicles', '1shrooms', '1garbage', '1vehicles', '1shrooms', '1garbage', '2vehicles', '2vehicles','2vehicles', '2vehicles']
    
    models, active_model = espnow_manager.receive_models()
    
    if models[0] == 'None' or not models:
        models = [GO_BACK_PROMPT]
    else:
        models = [GO_BACK_PROMPT, *models]
    
    display_list = models[:PER_PAGE]
    active_model = models[0]
    step_y = 16
    
    current_page = 1
    
    cursor_y = 0
    
    offset_x = 20
    
    draw_page_counter(tft, current_page)

    tft.fill_rect(0, cursor_y, *MARKER_SIZE, st7789.WHITE)
    print(f'Len = {len(models)}')
        
    while True:
        for i, m in enumerate(display_list):
            if m == active_model:
                tft.text(font, m, offset_x, i * 16, st7789.RED)
            else:
                tft.text(font, m, offset_x, i * 16)
                

        # Update page number
        draw_page_counter(tft, current_page)
        
        # Potwierdzenie wyboru
        if not MODEL_BUTTON.value():
            if cursor_y == 0:
                print('Exited model menu')
                return 'None'
            print(f"Selected model {models[cursor_y]}")
            return models[cursor_y + (current_page - 1) * PER_PAGE]
            time.sleep(0.2)

        # Scroll w dol
        if not AP_BUTTON.value():
            tft.fill(st7789.BLACK)
            cursor_y += 1
                
            print(cursor_y + (current_page-1) * PER_PAGE)
            
            if cursor_y >= PER_PAGE:
                current_page += 1

                cursor_y = 0
                display_list = [GO_BACK_PROMPT]
                for m in models[(current_page-1)*PER_PAGE:current_page*PER_PAGE]:
                    display_list.append(m)
                    
            if cursor_y + (current_page-1) * PER_PAGE > len(models):
                display_list = models[:PER_PAGE]
                current_page = 1
                cursor_y = 0

    
            tft.fill_rect(0, cursor_y * 16, *MARKER_SIZE, st7789.WHITE)
            time.sleep(0.2)
            
def show_prediction_results(tft, results):
    tft.fill(st7789.BLACK)
    
    if results[0] == "PREDICTION_FAIL":
        tft.text(font, "Prediction failed", 20, 16)
        tft.text(font, f"Error = {results[1]}", 20, 32)
    else:
        tft.text(font, "Prediction results", 20, 16)
        tft.text(font, f"Class = {results[0]}", 20, 32)
        tft.text(font, f"Accuracy = {results[1]}", 20, 48)


def connect_wifi(espnow_manager, ssid, password, sta, ap):
    espnow_manager.send_message("WIFI_CONNECT")
    espnow_manager.send_wifi_credentials(ssid, password)

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
    service = CredentialsService(AP_SSID, AP_PASSWORD, ap_if)
    
    service.start_ap()
    ssid, password = service.wait_for_credentials()
    print(f'Received ssid = {ssid}, password = {password}')
    
    return (ssid, password)


def main():
#     camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
#     camera.framesize(camera.FRAME_240X240)
#     
#     buf = camera.capture()
#     
#     with open('img.jpg', 'wb') as f:
#         f.write(buf)

#     
# #     get_wifi_credentials(ap)
# 
#     peer = b'\xec\x62\x60\x9d\x03\xec'
#     
#     espnow_manager = ESPNowCommunicationManager(peer, sta)
#     
#     print('Sent request to connect to wifi')
#     message = connect_wifi(espnow_manager, SSID, PASSWORD, sta, ap)
#     print(f'Response from connect_wifi = {message}')
#  
#     
#     print('Sent request to get models')
#     espnow_manager.send_message("GET_MODELS")
#     models = espnow_manager.receive_models()
#     print(models)
# #           
#     print('Sent request to change model')
#     message = change_model(espnow_manager, 'garbage')
#     print(message)
#     
# #   print('Sent request to predict')
#     
#     message = predict(espnow_manager, camera, 'img.jpg')
#     print(message)
#     time.sleep(10)
#     peeee = espnow_manager._espnow.get_peer(peer)
#     print(peeee)
#     
#     message = predict(espnow_manager, camera, 'img.jpg')
#     print(message)
#     message = predict(espnow_manager, camera, 'img.jpg')
#     print(message)

    
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
    
    # Network init =======================================
    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    ap.active(True)
    sta.active(True)
    sta.config(channel=1, reconnects=0)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()
    while sta.isconnected():
        time.sleep(0.1)
        
    # End network init ====================================
    
    # Screen init =========================================
    tft = config(0)
    tft.init()
    tft.fill(st7789.BLACK)
    
    # End screen init =====================================
    
    # Camera init =========================================
    
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
    camera.framesize(camera.FRAME_240X240)
    
    # End camera init =====================================
    
    # ESP NOW init ========================================
    peer = b'\xec\x62\x60\x9d\x03\xec'
    
    espnow_manager = ESPNowCommunicationManager(peer, sta)
    
    # End ESP NOW init ====================================
    start = utime.time()
        
    while True:
        if time.time() - start >= 30:
            return

        if not PREDICT_BUTTON.value():
            print('Prediction')
            buf = camera.capture()
            
            with open('prediction.jpg', 'wb') as f:
                f.write(buf)
                
                
            tft.jpg('prediction.jpg', 0, 0, st7789.SLOW)
                
            results = predict(espnow_manager, camera, 'prediction.jpg')

            show_prediction_results(tft, results)
            
            print(message)
            
            time.sleep(0.5)
            
        if not MODEL_BUTTON.value():
            print('Model menu')
            model = change_active_model(tft)
            
            if model != 'None':
                message = change_model(espnow_manager, model)
            else:
                pass

            time.sleep(0.5)

        if not AP_BUTTON.value():
            print('Access point active')
            
            ssid, password = get_wifi_credentials(ap)
            
            message = connect_wifi(espnow_manager, ssid, password, sta, ap)
            print(f'Response from connect_wifi = {message}')
            time.sleep(0.5)
        
        
    camera.deinit()
