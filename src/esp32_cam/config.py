microsd_config = {
    'directory': '/sd'
}

config = {
    'input_dims': (1, 224, 224, 3),
    'output_dims': (1, 7),
    'labels_path': 'sd/labels.txt',
    'path': 'sd/model.tflite',
    'arena_size': 1600 * 1024
}

