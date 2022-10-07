from utils import dims_to_size, get_file_size
import microlite
mode = 1
import jpglib
import gc

# TODO: Add logging and config validation
# TODO: Add model reloading option
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
        row_bytes = 240*3
        model_width = self.config.width * 3
        y_offset = (240 - self.config.height)//2 * row_bytes
        x_offset = (row_bytes - model_width)//2 * model_width
        
        for i in range (0, input_size):
            buffer_index = ((x_offset) + i%model_width + (i//model_width)*row_bytes) + y_offset
            input_tensor.setValue(i, self.model.input_buffer[buffer_index])
            
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
        print("before jpg read")
        print(gc.mem_free())
        self.model.read_jpg(image_path)
        print("after jpg read")
        print(gc.mem_free())
        self.interpreter.invoke()
        print("after interpreter")
        print(gc.mem_free())
#         TODO: FREE MEMORY??
        
    def init_interpreter(self):
        """
        Microlite interpreter initialization
        """
        self.interpreter = microlite.interpreter(self.model.model_buffer, self.config.arena_size, self.input_callback, self.output_callback) # Experimental arena size
        
class Model:
    def __init__(self, model_size, input_size):
        self.model_buffer = bytearray(model_size)
        self.input_buffer = None
        
    def read_model(self, model_path):
        """
        Read model from given path to memory
        
        :param model_path: model to be loaded
        """
        file = open(model_path, 'rb')
        file.readinto(self.model_buffer)
        file.close()
        
    def read_jpg(self, file_path):
        """
        Read file from given path to memory
        
        :param file_path: file to be loaded
        """
        self.input_buffer, _, _ = jpglib.decompress_jpg(file_path)
        print(type(self.input_buffer))
        print(len(self.input_buffer))
        print(self.input_buffer[0])
        print(self.input_buffer[1])
        print(self.input_buffer[2])
    
class ModelConfig:
    def __init__(self, model_config):
        if type(model_config) != dict:
            raise Exception("model_config should be type dict")
        
        if 'input_dims' not in model_config:
            raise Exception("model_config requires input_dims key")
        if len(model_config['input_dims']) != 4:
            raise Exception("input_dims needs to be length 4")
        if 'output_dims' not in model_config:
            raise Exception("model_config requires output_dims key")
        if len(model_config['output_dims']) != 2:
            raise Exception("output_dims needs to be length 2")
        if 'path' not in model_config:
            raise Exception("model_config requires path key")
        if 'arena_size' not in model_config:
            raise Exception("model_config requires arena_size key")
        
        self.input_size = dims_to_size(model_config['input_dims'])
        self.width = model_config['input_dims'][2]
        self.height = model_config['input_dims'][1]
        
        self.output_size = dims_to_size(model_config['output_dims'])
        self.class_num = model_config['output_dims'][1]
        
        self.path = model_config['path']
        
        self.size = get_file_size(self.path)
        
        self.arena_size = model_config['arena_size']
        
        if 'labels_path' in model_config:
            self.labels_path = model_config['labels_path']
        else:
            self.labels_path = None
        

