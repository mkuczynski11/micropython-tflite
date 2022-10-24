import utime
import network
import ntptime
import uos

from utils import singleton
from config import TMP_MODEL_PATH_DIR, MODELS_PATH, IMAGES_PATH

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
        for file in uos.listdir(TMP_MODEL_PATH_DIR):
            uos.remove(TMP_MODEL_PATH_DIR + '/' + file)
        
    def is_able_to_create_model(self):
        return self.model_passed and self.labels_passed
    
    def remove_model(self, model):
        for file in uos.listdir(MODELS_PATH + '/' + model):
            uos.remove(MODELS_PATH + '/' + model + '/' + file)
        uos.rmdir(MODELS_PATH + '/' + model)
        for class_name in uos.listdir(IMAGES_PATH + '/' + model):
            for file in uos.listdir(IMAGES_PATH + '/' + model + '/' + class_name):
                uos.remove(IMAGES_PATH + '/' + model + '/' + class_name + '/' + file)
            uos.rmdir(IMAGES_PATH + '/' + model + '/' + class_name)
        uos.rmdir(IMAGES_PATH + '/' + model)
    
    def move_model_from_tmp_folder(self, model_name):
        uos.rename(TMP_MODEL_PATH_DIR, MODELS_PATH + '/' + model_name)
        uos.mkdir(TMP_MODEL_PATH_DIR)
        
        uos.mkdir(IMAGES_PATH + '/' + model_name)
        f = open(MODELS_PATH + '/' + model_name + '/labels.txt')
        lines = f.readlines()
        for line in lines:
            uos.mkdir(IMAGES_PATH + '/' + model_name + '/' + line.strip())
        f.close()
        
        self.model_passed = False
        self.labels_passed = False
        
    def remove_images_for_model(self, model):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return False
        
        for class_name in uos.listdir(f'{IMAGES_PATH}/{model}'):
            for f in uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'):
                uos.remove(f'{IMAGES_PATH}/{model}/{class_name}/{f}')
                
        return True
    
    def remove_images_for_class(self, model, class_name):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return False
        
        class_dirs = uos.listdir(f'{IMAGES_PATH}/{model}')
        if class_name not in class_dirs:
            return False
        
        for f in uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'):
            uos.remove(f'{IMAGES_PATH}/{model}/{class_name}/{f}')
            
        return True
