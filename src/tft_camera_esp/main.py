import camera
from machine import Pin, SPI
import st7789
import network
from espnow_utils import ESPNowCommunicationManager
import time
import utime
from ap_service import CredentialsService
import vga1_16x16 as font

SSID = "iPhone"
PASSWORD = "12345678"

AP_SSID = "MP_AP"
AP_PASSWORD = "12345678"

# Set pins to correct ones
PREDICT_BUTTON = Pin(3, Pin.IN) # YELLOW  | predict
MODEL_BUTTON = Pin(1, Pin.IN, Pin.PULL_UP) # MIDDLE RED | open model menu / choose 

mosi = 13 # zielony -> 13 (DIN)
sck = 14 # pomaranczowy -> 14 (CLK)
cs = 15 # zolty -> 15 (CS)
dc = 12 # niebieski -> 12 (DC)
rst = 2 # brazowy -> 2 (RST)
baud = 31250000

MARKER_SIZE = (16, 16)
PER_PAGE = 12 # There can be only 15 positions in the list to display
GO_BACK_PROMPT = '> Go back'

APP_EXECUTION_LIMIT = 600 # seconds


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

def change_active_model(tft, espnow_manager):
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
            
    espnow_manager.send_message("GET_MODELS")
    available_models, active_model = espnow_manager.receive_models()
    
    if available_models[0] == 'None' or not available_models:
        models = [GO_BACK_PROMPT]
    else:
        models = [GO_BACK_PROMPT]
        for model in available_models:
            models.append(model)
    
    display_list = models[:PER_PAGE]
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
        if not PREDICT_BUTTON.value():
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

    print('Main function started')
    
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
    tft.fill(st7789.RED)
    tft.text(font, "Main started", 20, 16)
    
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
    service_active = False
    service_ip = None
    print('Main loop started')    
    while True:
        time_passed = time.time() - start
        if time_passed >= APP_EXECUTION_LIMIT:
            tft.fill(st7789.BLUE)
            tft.text(font, "App finished", 10, 48)
            break

        tft.fill(st7789.RED)
        tft.text(font, "Click button", 10, 32)
        tft.text(font, "Time left (s):", 10, 48)
        tft.text(font, f"{APP_EXECUTION_LIMIT - time_passed}", 10, 64)
        time.sleep(0.2)
        if service_ip and service_active:
            tft.text(font, "Service IP:", 10, 80)
            tft.text(font, f"{service_ip}", 10, 96)

        
        if not PREDICT_BUTTON.value() and not MODEL_BUTTON.value():
            print('Access point active')
            tft.fill(st7789.BLACK)
            tft.text(font, "AP active", 10, 16)
            tft.text(font, "AP service:", 10, 32)
            tft.text(font, f"{AP_SSID}", 10, 48)
            tft.text(font, "192.168.4.1", 10, 48)
            ssid, password = get_wifi_credentials(ap)
            
            if not ssid or not password:
                tft.fill(st7789.BLACK)
                tft.text(font, "Failed to get", 10, 16)
                tft.text(font, "WiFi credentials", 10, 32)
                time.sleep(2)
                continue

            message, ip = connect_wifi(espnow_manager, ssid, password, sta, ap)
            print(f'Response from connect_wifi = {message}')
            tft.fill(st7789.BLACK)
            tft.text(font, f"{message}", 10, 16)
            if ip:
                tft.text(font, f"{ip}", 10, 32)
                service_active = True
            service_ip = ip
        
            time.sleep(7)


        if not PREDICT_BUTTON.value():
            print('Prediction')
            tft.fill(st7789.BLACK)
            tft.text(font, "Prediction running", 20, 16)

            buf = camera.capture()
            
            with open('prediction.jpg', 'wb') as f:
                f.write(buf)
                
            tft.jpg('prediction.jpg', 0, 0, st7789.SLOW)
                
            results = predict(espnow_manager, camera, 'prediction.jpg')

            tft.fill(st7789.BLACK)
    
            if results[0] == "PREDICTION_FAIL":
                tft.text(font, "Predict failed", 10, 16)
                tft.text(font, "Error:", 10, 32)
                tft.text(font, f"{results[1]}:", 10, 48)
            else:
                tft.text(font, "Class:", 10, 16)
                tft.text(font, f"{results[0]}", 10, 32)
                tft.text(font, "Accuracy:", 10, 48)
                tft.text(font, f"{results[1]}", 10, 64)
                
            time.sleep(4)
            
        if not MODEL_BUTTON.value():
            print('Model menu')
            tft.fill(st7789.BLACK)
            tft.text(font, "Model menu", 20, 16)
            time.sleep(2)
            
            model = change_active_model(tft, espnow_manager)
            
            if model != 'None':
                message = change_model(espnow_manager, model)
            else:
                continue

            time.sleep(0.5)
        
        
    camera.deinit()

main()
