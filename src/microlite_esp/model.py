from utils import (
    dims_to_size,
    get_file_size,
    singleton,
    ResponseCode)
import microlite
mode = 1
import jpglib
from config import (
    MODELS_PATH,
    TMP_IMAGE_PATH,
    MODEL_INFO_FILE_NAME,
    LABELS_FILE_NAME,
    MODEL_FILE_NAME
)
import uos

class ModelExecutor:
    def __init__(self, model, model_config, input_callback=None, output_callback=None):
        self.model = model
        self.config = model_config
        if input_callback == None:
            self.input_callback = self.base_input_callback
        if output_callback == None:
            self.output_callback = self.base_output_callback
        self.predicted_class = ""
        self.prediction_score = 0
        
    def base_input_callback(self, microlite_interpreter):
        """
        Function to call while populating model's input tensors.
        """
        input_tensor = microlite_interpreter.getInputTensor(0)
        
        input_size = self.config.width * self.config.height * 3
        
        for i in range (0, input_size):
            input_tensor.setValue(i, self.model.input_buffer[i])
    
    def base_output_callback(self, microlite_interpreter):
        """
        Function to call while reading results from model's output tensors.
        """
        output_tensor = microlite_interpreter.getOutputTensor(0)
        
        output_size = self.config.class_num
        
        best_index = 0
        best_value = -1
        text = "Prediction=["
        
        for i in range(output_size):
            value = output_tensor.getValue(i)
            if value > best_value:
                best_index = i
                best_value = value
                
            text += self.config.labels[i]
            text += " "
            text += str(output_tensor.getValue(i))
            text += " "
        text += "]"
        
        self.predicted_class = self.config.labels[best_index]
        self.prediction_score = best_value
  
    def predict(self):
        """
        Run prediction on image from the given path.
        
        :param image_path: path pointing to an image to predict on
        """
        self.model.read_jpg(TMP_IMAGE_PATH)
        
        self.model.resize_input(self.config.width, self.config.height, 240, 240)
        
        self.interpreter.invoke()
        
        return (self.predicted_class, self.prediction_score)
        
    def init_interpreter(self):
        """
        Microlite interpreter initialization.
        """
        self.interpreter = microlite.interpreter(self.model.model_buffer, self.config.arena_size, self.input_callback, self.output_callback)
        
class Model:
    def __init__(self, model_size, input_size):
        self.model_buffer = bytearray(model_size)
        self.input_buffer = None
        
    def read_model(self, model_path):
        """
        Read model from given path to memory.
        
        :param model_path: model to be loaded
        """
        file = open(model_path, 'rb')
        file.readinto(self.model_buffer)
        file.close()
        
    def read_jpg(self, file_path):
        """
        Read file from given path to memory.
        
        :param file_path: file to be loaded
        """
        self.input_buffer = None
        self.input_buffer, _, _ = jpglib.decompress_jpg(file_path)
        
    def resize_input(self, out_w, out_h, src_w, src_h):
        self.input_buffer = jpglib.resize_img(self.input_buffer, out_w, out_h, src_w, src_h)
        
    def reset_input_buffer(self):
        """
        Reset input buffer by freeing the memory.
        """
        self.input_buffer = None
    
class ModelConfig:
    def __init__(self, config_file_path):
        model_config = self.read_config_file(config_file_path)
        self.name = model_config['name']
        
        self.width = model_config['image_width']
        self.height = model_config['image_height']
        self.channels = 3
        self.batch_size = 1
        
        self.input_dims = (self.batch_size, self.height, self.width, self.channels)
        self.input_size = dims_to_size(self.input_dims)
        
        self.path = model_config['path']
        self.size = get_file_size(self.path)
        
        self.labels = []
        self.labels_path = model_config['labels_path']
        self.read_labels()
        self.class_num = len(self.labels)
        
        self.arena_size = model_config['arena_size']
        
    def read_config_file(self, file_path):
        config = {}
        
        config['name'] = file_path.split('/')[-2]
        model_dir = file_path[0:file_path.rfind('/')]
        config['path'] = f'{model_dir}/{MODEL_FILE_NAME}'
        config['labels_path'] = f'{model_dir}/{LABELS_FILE_NAME}'
        f = open(file_path, 'r')
        lines = f.readlines()
        config['image_width'] = int(lines[0])
        config['image_height'] = int(lines[1])
        config['arena_size'] = int(lines[2])
        
        return config
        
    def read_labels(self):
        """
        Read labels from a given path into list.
        """
        
        file = open(self.labels_path, 'r')
        lines = file.readlines()
        for line in lines:
            self.labels.append(line.strip())
        file.close()

@singleton
class ModelManager:
    def __init__(self, model_executor=None):
        self.model_executor = model_executor
        self.active_model_name = None
        
    def reload_model(self, model_executor):
        """
        Reload model with other initialized executor
        :param model_executor: initialized model_executor with interpreter
        """
        self.model_executor = model_executor
        self.active_model_name = model_executor.config.name
        
    def unload_model(self):
        self.model_executor = None
        self.active_model_name = None
        
    def load_model(self, model_name):
        if model_name not in uos.listdir(f'{MODELS_PATH}'):
            return ResponseCode.MODEL_NOT_FOUND
        
        self.unload_model()
        
        model_config = ModelConfig(f'{MODELS_PATH}/{model_name}/{MODEL_INFO_FILE_NAME}')
        model = Model(model_config.size, model_config.input_size)
        model.read_model(model_config.path)
        model_executor = ModelExecutor(model, model_config)
        model_executor.init_interpreter()
        
        self.reload_model(model_executor)
        
        return ResponseCode.OK
        
    def is_loaded(self):
        return self.active_model_name != None
