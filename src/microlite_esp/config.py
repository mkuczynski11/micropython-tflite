# MicroSD card configuration
MICROSD_DIRECTORY = '/sd'
MODELS_PATH = MICROSD_DIRECTORY + '/models'
IMAGES_PATH = MICROSD_DIRECTORY + '/static/images'
TMP_IMAGE_PATH = MICROSD_DIRECTORY + '/tmp'

# Model configuration
# TODO: Move arena size to logic
# TODO: Make sure all folders are created when sending model into esp
config = {
    'name': "muschrooms",
    'image_width': 224,
    'image_height': 224,
    'labels_path': 'sd/models/muschrooms/labels.txt',
    'path': 'sd/models/muschrooms/model.tflite',
    'arena_size': 800000
}



