import camera
from machine import Pin, SPI
import st7789
import network
from espnow_utils import ESPNowCommunicationManager
import time
import utime
from ap_service import CredentialsService
import vga1_16x16 as font
import uos

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

def change_active_model(tft, espnow_manager, sta, ap):
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
    if not sta.isconnected(): 
        sta, ap = reset_wifi()
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
                return GO_BACK_PROMPT
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
    if not sta.isconnected():
        sta, ap = reset_wifi()
    espnow_manager.send_wifi_credentials(ssid, password)

    start = utime.time()
    timed_out = False
        
    if not sta.isconnected():
        sta.active(True)
        sta.connect(ssid, password)
        while not sta.isconnected() and not timed_out:
            if utime.time() - start >= 20:
                timed_out = True
            else:
                pass

    if sta.isconnected():
        ap.active(True)
        print(f'Active channel is {sta.config("channel")}')
    else:
        pass
    
    message = espnow_manager.receive_message()
    ip = None

    if message == "WIFI_CONNECT_SUCCESS":
        ip = espnow_manager.receive_text()
    
    return (message, ip)

    
def change_model(espnow_manager, model_name, sta, ap):
    espnow_manager.send_message("CHANGE_MODEL")
    if not sta.isconnected():
        sta, ap = reset_wifi()
    espnow_manager.send_model_name(model_name)
    
    message = espnow_manager.receive_message()
    
    if message == "CHANGE_MODEL_FAIL":
        message = espnow_manager.receive_text()
    
    return message
    
def predict(espnow_manager, camera, file_name, sta, ap):        
    espnow_manager.send_prediction_request(file_name, sta, ap)

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


def get_wifi_credentials(sta, ap):
    ap.active(False)
    ap.active(True)
    service = CredentialsService(AP_SSID, AP_PASSWORD, ap)
    
    service.start_ap()
    ssid, password = service.wait_for_credentials()
    print(f'Received ssid = {ssid}, password = {password}')
    if not sta.isconnected():
        sta, ap = reset_wifi()
    return (ssid, password)

def reset_wifi():
    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    sta.active(True)
    ap.active(True)
    sta.config(channel=1, reconnects=0)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()
    while sta.isconnected():
        time.sleep(0.1)
        
    return sta, ap

def main():   
    print('Main function started')
    time.sleep(5)
    
    # Network init =======================================
    sta, ap = reset_wifi()
        
    # End network init ====================================
    
    # Screen init =========================================
    tft = config(0)
    tft.init()
    
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
    ap_invoked = False
    print('Main loop started')
    refresh_view = True
    while True:
        
        time.sleep(0.2)

        if refresh_view:
            tft.fill(st7789.BLACK)
            tft.text(font, "RED button:", 10, 16)
            tft.text(font, "> Prediction:", 10, 32)
            tft.text(font, "YELLOW button:", 10, 48)
            tft.text(font, "> Change model", 10, 64)
            tft.text(font, "BOTH pressed:", 10, 80)
            tft.text(font, "> AP Service", 10, 96)
            
            refresh_view = False
    
            if service_ip and service_active:
                tft.text(font, "Service IP:", 10, 112)
                tft.text(font, f"{service_ip}", 10, 128)
        
        if not PREDICT_BUTTON.value() and not MODEL_BUTTON.value():
            print('Access point active')
            if not ap_invoked:
                tft.fill(st7789.BLACK)
                tft.text(font, "AP active", 10, 16)
                tft.text(font, "AP service:", 10, 32)
                tft.text(font, f"{AP_SSID}", 10, 48)
                tft.text(font, "192.168.4.1", 10, 64)
                ssid, password = get_wifi_credentials(sta, ap)
                
                if not ssid or not password:
                    tft.fill(st7789.BLACK)
                    tft.text(font, "Failed to get", 10, 16)
                    tft.text(font, "WiFi login", 10, 32)
                    time.sleep(2)
                    continue

                message, ip = connect_wifi(espnow_manager, ssid, password, sta, ap)
                print(f'Response from connect_wifi = {message}')
                
                if message == "WIFI_CONNECT_SUCCESS":
                    tft.fill(st7789.BLACK)
                    tft.text(font, f"Connected", 10, 16)
                    tft.text(font, f"to WiFi", 10, 32)
                elif message == "WIFI_CONNECT_FAIL":
                    tft.fill(st7789.BLACK)
                    tft.text(font, "Failed to", 10, 16)
                    tft.text(font, "connect to WIFI", 10, 32)
                else:
                    tft.fill(st7789.BLACK)
                    tft.text(font, "Error!", 10, 16)
                    tft.text(font, "Consider reset", 10, 32)
                    
                if ip:
                    tft.text(font, f"{ip}", 10, 48)
                    service_active = True
                service_ip = ip
                ap_invoked = True
                
            else:
                tft.fill(st7789.BLACK)
                tft.text(font, "AP can be only", 10, 16)
                tft.text(font, "started once", 10, 32)
            
            refresh_view = True
        
            time.sleep(4)


        if not PREDICT_BUTTON.value():
            print('Prediction')
            tft.fill(st7789.BLACK)

            buf = camera.capture()
            buf = camera.capture()

            f = open('prediction.jpg', 'wb')
            f.write(buf)
            f.close()
            tft.jpg('prediction.jpg', 0, 0, st7789.FAST)

            tft.text(font, "Predicting", 10, 32)
                
            results = predict(espnow_manager, camera, 'prediction.jpg', sta, ap)
            
            uos.remove('prediction.jpg')

            tft.fill(st7789.BLACK)
    
            if results[0] == "PREDICTION_FAIL":
                tft.text(font, "Predict failed", 0, 16)
                tft.text(font, "Error:", 0, 32)
                tft.text(font, f"{results[1]}:", 0, 48)
            else:
                tft.text(font, "Class:", 10, 16)
                tft.text(font, f"{results[0]}", 10, 32)
                tft.text(font, "Accuracy:", 10, 48)
                tft.text(font, f"{results[1]}", 10, 64)
                
            refresh_view = True
            time.sleep(10)
            
        if not MODEL_BUTTON.value():
            print('Model menu')
            
            # Handle cursor scrolling one position under list
            model = change_active_model(tft, espnow_manager, sta, ap)
                
            if model == GO_BACK_PROMPT:
                tft.fill(st7789.BLACK)
                tft.text(font, "Exited from", 20, 16)
                tft.text(font, "model menu", 20, 32)
                
            elif model != 'None':
                message = change_model(espnow_manager, model, sta, ap)
                
                if message == "CHANGE_MODEL_SUCCESS":
                    tft.fill(st7789.BLACK)
                    tft.text(font, "Model changed", 20, 16)
                    tft.text(font, "Active model:", 20, 32)
                    tft.text(font, f"{model}", 20, 48)
                else:
                    tft.fill(st7789.BLACK)
                    tft.text(font, "Failed to", 20, 16)
                    tft.text(font, "change model", 20, 32)
                
            refresh_view = True
            time.sleep(5)        
        
    camera.deinit()

main()