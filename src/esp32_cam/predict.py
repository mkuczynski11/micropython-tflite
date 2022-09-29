def main():
    print("Starting main function")
    
    from config import config
    from model import ModelConfig, Model, ModelExecutor
    
    model_config = ModelConfig(config)
    model = Model(model_config.size, model_config.input_size)
    model.read_model(model_config.path)
    model_executor = ModelExecutor(model, model_config)
    model_executor.init_interpreter()

    print("Classify muschroom")
    model_executor.predict('maslak')
    print("Ending main function")

main()

