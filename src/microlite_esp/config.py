# MicroSD card configuration
MICROSD_DIRECTORY = '/sd'
MODELS_PATH = MICROSD_DIRECTORY + '/models'
IMAGES_PATH = MICROSD_DIRECTORY + '/static/images'
TMP_IMAGE_PATH_DIR = MICROSD_DIRECTORY + '/tmp'
TMP_IMAGE_PATH = MICROSD_DIRECTORY + '/tmp/image.jpg'
TMP_MODEL_PATH_DIR = MICROSD_DIRECTORY + '/tmp/model'
TMP_MODEL_PATH = MICROSD_DIRECTORY + '/tmp/model/model.tflite'
TMP_LABELS_PATH = MICROSD_DIRECTORY + '/tmp/model/labels.txt'
TMP_INFO_PATH = MICROSD_DIRECTORY + '/tmp/model/info.txt'

# Memory constants
MAX_MODEL_RAM_USAGE = 3_500_000 # Size in bytes

# Frontend constants
IMAGES_ON_PAGE = 5
