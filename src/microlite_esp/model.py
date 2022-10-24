from utils import (
    dims_to_size,
    get_file_size,
    singleton)
import microlite
mode = 1
import jpglib
from config import (
    MODELS_PATH,
    IMAGES_PATH,
    TMP_IMAGE_PATH
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
            
    def base_input_callback(self, microlite_interpreter):
        """
        Function to call while populating model's input tensors.
        """
        input_tensor = microlite_interpreter.getInputTensor(0)
        
        input_size = self.config.width * self.config.height * 3
        
        for i in range (0, input_size):
            input_tensor.setValue(i, self.model.input_buffer[i])
            
        print ("setup %d bytes on the inputTensor." % (input_size))
    
    def base_output_callback(self, microlite_interpreter):
        """
        Function to call while reading results from model's output tensors.
        """
        output_tensor = microlite_interpreter.getOutputTensor(0)
        
        output_size = self.config.class_num
        
        best_index = 0
        text = "Prediction=["
        
        for i in range(output_size):
            value = output_tensor.getValue(i)
            if value > output_tensor.getValue(best_index):
                best_index = i
                
            text += self.config.labels[i]
            text += " "
            text += str(output_tensor.getValue(i))
            text += " "
        text += "]"
        
        print(text)
        
        self.predicted_class = self.config.labels[best_index]
  
    def predict(self, image_path):
        """
        Run prediction on image from the given path.
        
        :param image_path: path pointing to an image to predict on
        """
        self.model.read_jpg(image_path)
        self.model.resize_input(self.config.width, self.config.height, 240, 240)
        self.interpreter.invoke()
        return self.predicted_class
        
    def init_interpreter(self):
        """
        Microlite interpreter initialization.
        """
        self.interpreter = microlite.interpreter(self.model.model_buffer, self.config.arena_size, self.input_callback, self.output_callback) # Experimental arena size
        
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
        size, self.input_buffer, _, _ = jpglib.decompress_jpg(file_path)
        
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
        config['path'] = model_dir + '/model.tflite'
        config['labels_path'] = model_dir + '/labels.txt'
        f = open(file_path)
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
        self.models_path = MODELS_PATH
        self.images_path = IMAGES_PATH
        self.current_image_path = TMP_IMAGE_PATH
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
        
    def load_from_path(self, model_path):
        model_config = ModelConfig(model_path + '/info.txt')
        model = Model(model_config.size, model_config.input_size)
        model.read_model(model_config.path)
        model_executor = ModelExecutor(model, model_config)
        model_executor.init_interpreter()
        
        self.reload_model(model_executor)
        
    def is_loaded(self):
        return self.active_model_name != None
        
    def predict_scenario(self):
        """
        Reload model with other initialized executor
        :param image_path: path pointing to an image to predict on
        """
        image = mock_file_exchange()
        # Save jpg to file
        f = open(self.current_image_path, 'wb')
        f.write(image)
        f.close()
        # Run prediction on the file
        class_name = self.model_executor.predict(self.current_image_path)
        # Rename and move the file
        model_name = self.model_executor.config.name
        classified_count = len(uos.listdir(self.images_path + '/' + model_name + '/' + class_name))
        uos.rename(self.current_image_path, self.images_path + '/' + model_name + '/' + class_name + '/' + class_name + str(classified_count + 1) + '.jpg')

    def change_model_scenario():
        pass

    def send_models_info_scenario():
        pass

def mock_file_exchange():
    src = open('sd/static/images/muschrooms/Suillus/Suillus1.jpg', 'rb')
    buf = src.read()
    src.close()
    return buf
