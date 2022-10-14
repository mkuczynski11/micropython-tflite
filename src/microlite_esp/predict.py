import time
import gc

from config import config, MICROSD_DIRECTORY
from model import ModelConfig, Model, ModelExecutor

def mock_file_exchange():
    time.sleep(5)
    src = open('mas.jpg', 'rb')
    buf = src.read()
    src.close()
    return buf
    

# TODO: Create ModelManager which will communicate with other esp/computer
#       and will handle this esp main loop
def main():
    print("Starting main function")

    # TODO: This should be created when user picks the model
    model_config = ModelConfig(config)
    model = Model(model_config.size, model_config.input_size)
    model.read_model(model_config.path)
    model_executor = ModelExecutor(model, model_config)
    model_executor.init_interpreter()
    
    while True:
        # TODO: Wait for esp-now msg with picture made on esp32-cam
        image = mock_file_exchange()
        # Save jpg to file
        image_path = MICROSD_DIRECTORY + '/tmp/image.jpg'
        f = open(image_path, 'wb')
        f.write(image)
        f.close()
        # Run prediction on the file
        class_name = model_executor.predict(image_path)
        # Rename and move the file
        classified_count = len(uos.listdir(MICROSD_DIRECTORY + '/images/muschrooms/' + class_name))
        uos.rename(image_path, MICROSD_DIRECTORY + '/images/muschrooms/' + class_name + '/' + class_name + str(classified_count + 1) + '.jpg')
        
    print("Ending main function")

main()




