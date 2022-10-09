# MicroSD card configuration
microsd_config = {
    'directory': '/sd'
}

# Model configuration
# TODO: Move arena size to logic
# TODO: Add possibility to add more models configurations
# TODO: Add guide to defining parameters
config = {
    'input_dims': (1, 224, 224, 3),
    'output_dims': (1, 7),
    'labels_path': 'sd/labels.txt',
    'path': 'sd/model_q.tflite',
    'arena_size': 800000
}


