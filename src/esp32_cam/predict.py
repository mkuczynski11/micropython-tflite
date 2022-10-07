import camera
import time
import gc

from config import config
from model import ModelConfig, Model, ModelExecutor

def take_picture():
        buf = camera.capture()
        print("Picture taken. Saving to file")
        print(len(buf))
        f = open('sd/pic.jpg', 'w')
        f.write(buf)
        f.close()
        print("File closed")

def main():
    print("Starting main function")

    model_config = ModelConfig(config)
    model = Model(model_config.size, model_config.input_size)
    model.read_model(model_config.path)
    model_executor = ModelExecutor(model, model_config)
    model_executor.init_interpreter()

    camera.init(0, format=camera.JPEG)
    camera.set_framesize(camera.FRAME_240X240)

#     while True:
#     print("Picture will be taken in 5 seconds")
#     time.sleep(5)
    
    print("before take_picture")
    print(gc.mem_free())
    take_picture()
    print("after take_picture")
    gc.collect()
    print(gc.mem_free())

    print("Prediction starting")
    model_executor.predict('sd/pic.jpg')
    print("Prediction ending")
    
    camera.deinit()
    
    print("Ending main function")

main()



