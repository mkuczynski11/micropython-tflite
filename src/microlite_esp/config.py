# MicroSD card configuration
MICROSD_DIRECTORY = '/sd'

# Model configuration
# TODO: Move arena size to logic
# TODO: Add possibility to add more models configurations
# TODO: Such configuration should be send on model transfer from computer
# TODO: Make sure all folders are created when sending model into esp
config = {
    'image_width': 224,
    'image_height': 224,
    'labels_path': 'sd/models/muschrooms/labels.txt',
    'path': 'sd/models/muschrooms/model.tflite',
    'arena_size': 800000
}




