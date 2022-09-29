from utils import dims_to_size, get_file_size
import microlite
mode = 1

class ModelExecutor:
    def __init__(self, model, model_config, input_callback=None, output_callback=None):
        self.model = model
        self.config = model_config
        if input_callback == None:
            self.input_callback = self.base_input_callback
        if output_callback == None:
            self.output_callback = self.base_output_callback
            
    def base_input_callback(self, microlite_interpreter):
        """
        Function to call while populating model's input tensors
        """
        input_tensor = microlite_interpreter.getInputTensor(0)
        
        input_size = self.config.input_size
        
        for i in range (0, input_size):
            input_tensor.setValue(i, self.model.input_buffer[i])
            
        print ("setup %d bytes on the inputTensor." % (input_size))
    
    def base_output_callback(self, microlite_interpreter):
        """
        Function to call while reading results from model's output tensors
        """
        output_tensor = microlite_interpreter.getOutputTensor(0)
        
        output_size = self.config.output_size
        
        text = "Prediction=["
        
        for i in range(output_size):
            text += str(output_tensor.getValue(i))
            text += " "
        text += "]"
        
        print(text)
  
    def predict(self, image_path):
        """
        Run prediction on image from the given path
        
        :param image_path: path pointing to an image to predict on
        """
        self.model.read_file(image_path)
        self.interpreter.invoke()
        
    def init_interpreter(self):
        """
        Microlite interpreter initialization
        """
        self.interpreter = microlite.interpreter(self.model.model_buffer, self.config.arena_size, self.input_callback, self.output_callback) # Experimental arena size
        
class Model:
    def __init__(self, model_size, input_size):
        self.model_buffer = bytearray(model_size)
        self.input_buffer = bytearray(input_size)
        
    def read_model(self, model_path):
        """
        Read model from given path to memory
        
        :param model_path: model to be loaded
        """
        file = open(model_path, 'rb')
        file.readinto(self.model_buffer)
        file.close()
        
    def read_file(self, file_path):
        """
        Read file from given path to memory
        
        :param file_path: file to be loaded
        """
        file = open(file_path, 'rb')
        file.readinto(self.input_buffer)
        file.close()
    
class ModelConfig:
    def __init__(self, model_config):
        if type(model_config) != dict:
            raise Exception("model_config should be type dict")
        
        if 'input_dims' not in model_config:
            raise Exception("model_config requires input_dims key")
        if 'output_dims' not in model_config:
            raise Exception("model_config requires output_dims key")
        if 'path' not in model_config:
            raise Exception("model_config requires path key")
        if 'arena_size' not in model_config:
            raise Exception("model_config requires arena_size key")
        
        self.input_size = dims_to_size(model_config['input_dims'])
        self.output_size = dims_to_size(model_config['output_dims'])
        
        self.path = model_config['path']
        
        self.size = get_file_size(self.path)
        
        self.arena_size = model_config['arena_size']
        
        if 'labels_path' in model_config:
            self.labels_path = model_config['labels_path']
        else:
            self.labels_path = None
        
