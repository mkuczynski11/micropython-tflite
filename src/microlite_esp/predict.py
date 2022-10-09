import time
import gc

from config import config
from model import ModelConfig, Model, ModelExecutor

def main():
    print("Starting main function")

    model_config = ModelConfig(config)
    model = Model(model_config.size, model_config.input_size)
    model.read_model(model_config.path)
    model_executor = ModelExecutor(model, model_config)
    model_executor.init_interpreter()

    print("Prediction starting")
    model_executor.predict('mas.jpg')
    print("Prediction ending")
    
    print("Ending main function")

main()


