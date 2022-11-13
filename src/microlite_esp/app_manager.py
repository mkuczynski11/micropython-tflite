import utime
import network
import uos
import microlite

from utils import singleton, get_free_space, get_file_size
from config import (
    TMP_MODEL_PATH_DIR, MODELS_PATH, IMAGES_PATH,
    MICROSD_DIRECTORY, MAX_MODEL_RAM_USAGE, TMP_MODEL_PATH,
    TMP_INFO_PATH, TMP_LABELS_PATH)

class ResponseCode:
    OK = "OK"
    NOT_ENOUGH_MEMORY = "SD card has reached its maximum memory"
    MODEL_NOT_FOUND = "model was not found"
    CLASS_NOT_FOUND = "class was not found"
    IMAGE_NOT_FOUND = "image was not found"

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
            sta_if.active(True)
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected() and not timed_out:
                if utime.time() - start >= 20:
                    timed_out = True
                else:
                    pass
        
        if sta_if.isconnected():
            return sta_if.ifconfig()
        else: 
            return ()
            
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
        if model not in uos.listdir(MODELS_PATH):
            return ResponseCode.MODEL_NOT_FOUND
        
        for file in uos.listdir(MODELS_PATH + '/' + model):
            uos.remove(MODELS_PATH + '/' + model + '/' + file)
        uos.rmdir(MODELS_PATH + '/' + model)
        for class_name in uos.listdir(IMAGES_PATH + '/' + model):
            for file in uos.listdir(IMAGES_PATH + '/' + model + '/' + class_name):
                uos.remove(IMAGES_PATH + '/' + model + '/' + class_name + '/' + file)
            uos.rmdir(IMAGES_PATH + '/' + model + '/' + class_name)
        uos.rmdir(IMAGES_PATH + '/' + model)
        
        return ResponseCode.OK
    
    def move_model_from_tmp_folder(self, model_name):
        uos.rename(TMP_MODEL_PATH_DIR, MODELS_PATH + '/' + model_name)
        uos.mkdir(TMP_MODEL_PATH_DIR)
        
        uos.mkdir(IMAGES_PATH + '/' + model_name)
        f = open(MODELS_PATH + '/' + model_name + '/labels.txt', 'r')
        lines = f.readlines()
        for line in lines:
            uos.mkdir(IMAGES_PATH + '/' + model_name + '/' + line.strip())
        f.close()
        
        self.model_passed = False
        self.labels_passed = False
        
    def remove_images_for_model(self, model):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return ResponseCode.MODEL_NOT_FOUND
        
        for class_name in uos.listdir(f'{IMAGES_PATH}/{model}'):
            for f in uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'):
                uos.remove(f'{IMAGES_PATH}/{model}/{class_name}/{f}')
                
        return ResponseCode.OK
    
    def remove_images_for_class(self, model, class_name):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return ResponseCode.MODEL_NOT_FOUND
        
        class_dirs = uos.listdir(f'{IMAGES_PATH}/{model}')
        if class_name not in class_dirs:
            return ResponseCode.CLASS_NOT_FOUND
        
        for f in uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'):
            uos.remove(f'{IMAGES_PATH}/{model}/{class_name}/{f}')
            
        return ResponseCode.OK
    
    def remove_image(self, model, class_name, file_name):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return ResponseCode.MODEL_NOT_FOUND
        
        class_dirs = uos.listdir(f'{IMAGES_PATH}/{model}')
        if class_name not in class_dirs:
            return ResponseCode.CLASS_NOT_FOUND
        
        file_list = uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}')
        if file_name not in file_list:
            return ResponseCode.IMAGE_NOT_FOUND
        
        uos.remove(f'{IMAGES_PATH}/{model}/{class_name}/{file_name}')
            
        return ResponseCode.OK
    
    def append_to_info_file_from_string_list(self, text_list):
        f = open(TMP_INFO_PATH, 'a')
        for text in text_list:
            if len(text) > get_free_space(MICROSD_DIRECTORY):
                f.close()
                return ResponseCode.NOT_ENOUGH_MEMORY
            f.write(text)
        
        f.close()
        return ResponseCode.OK
    
    def append_to_info_file_from_buffer(self, buffer):
        f = open(TMP_INFO_PATH, 'ab')
        if len(buffer) > get_free_space(MICROSD_DIRECTORY):
            f.close()
            return ResponseCode.NOT_ENOUGH_MEMORY
        
        f.write(buffer)
        f.close()
        return ResponseCode.OK
    
    def append_to_model_file_from_buffer(self, buffer):
        f = open(TMP_MODEL_PATH, 'ab')
        if len(buffer) > get_free_space(MICROSD_DIRECTORY):
            f.close()
            return ResponseCode.NOT_ENOUGH_MEMORY
        
        f.write(buffer)
        f.close()
        return ResponseCode.OK
    
    def create_labels_file_from_buffer(self, buffer):
        f = open(TMP_LABELS_PATH, 'wb')
        if len(buffer) > get_free_space(MICROSD_DIRECTORY):
            f.close()
            return ResponseCode.NOT_ENOUGH_MEMORY
        
        f.write(buffer)
        f.close()
        return ResponseCode.OK
    
    def get_model_list(self):
        return uos.listdir(MODELS_PATH)
    
    def get_class_list(self, model):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return (ResponseCode.MODEL_NOT_FOUND, [])
        return (ResponseCode.OK, uos.listdir(f'{IMAGES_PATH}/{model}'))
    
    def get_images_list(self, model, class_name):
        dirs = uos.listdir(IMAGES_PATH)
        if model not in dirs:
            return (ResponseCode.MODEL_NOT_FOUND, [])
        
        class_dirs = uos.listdir(f'{IMAGES_PATH}/{model}')
        if class_name not in class_dirs:
            return (ResponseCode.CLASS_NOT_FOUND, [])
        
        return (ResponseCode.OK, uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'))
    
    def get_image(self, model, class_name, file_name):
        if model not in uos.listdir(IMAGES_PATH):
            return (ResponseCode.MODEL_NOT_FOUND, "")
        elif class_name not in uos.listdir(f'{IMAGES_PATH}/{model}'):
            return (ResponseCode.CLASS_NOT_FOUND, "")
        elif file_name not in uos.listdir(f'{IMAGES_PATH}/{model}/{class_name}'):
            return (ResponseCode.IMAGE_NOT_FOUND, "")
        
        f = open(f'{IMAGES_PATH}/{model}/{class_name}/{file_name}', 'rb')
        buf = f.read()
        f.close()
        return (ResponseCode.OK, buf)
    
    def get_image_path(self, model, class_name, file_name):
        return f'{IMAGES_PATH}/{model}/{class_name}/{file_name}'
    
    def is_able_to_load_model(self, model_size):
        return model_size < MAX_MODEL_RAM_USAGE
    
    # TODO: validate in memorymanager
    def validate_required_memory(self, model_width, model_height):
        print('validating required memory')
        print(f'Max ram usage for model is {MAX_MODEL_RAM_USAGE}')
        arena_size_memory = MAX_MODEL_RAM_USAGE - (get_file_size(TMP_MODEL_PATH) + (int(model_width) * int(model_height) * 3))
        
        print(f'Model size is {get_file_size(TMP_MODEL_PATH)}')
        print(f'Memory for arena size left is {arena_size_memory}')
        model = bytearray(get_file_size(TMP_MODEL_PATH))
        file = open(TMP_MODEL_PATH, 'rb')
        file.readinto(model)
        file.close()
        try:
            interpreter = microlite.interpreter(model, arena_size_memory, None, None)
            return arena_size_memory
        except MemoryError:
            return 0
