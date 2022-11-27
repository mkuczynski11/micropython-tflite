# MicroSD card configuration
MICROSD_DIRECTORY = '/sd'
MODELS_PATH = MICROSD_DIRECTORY + '/models'
IMAGES_PATH = MICROSD_DIRECTORY + '/static/images'
TMP_IMAGE_PATH_DIR = MICROSD_DIRECTORY + '/tmp'
TMP_IMAGE_PATH = MICROSD_DIRECTORY + '/tmp/image.jpg'
TMP_MODEL_PATH_DIR = MICROSD_DIRECTORY + '/tmp/model'
MODEL_INFO_FILE_NAME = "info.txt"
LABELS_FILE_NAME = "labels.txt"
MODEL_FILE_NAME = "model.tflite"
TMP_MODEL_PATH = MICROSD_DIRECTORY + f'/tmp/model/{MODEL_FILE_NAME}'
TMP_LABELS_PATH = MICROSD_DIRECTORY + f'/tmp/model/{LABELS_FILE_NAME}'
TMP_INFO_PATH = MICROSD_DIRECTORY + f'/tmp/model/{MODEL_INFO_FILE_NAME}'
TMP_INTERPRETER_LOG_PATH = MICROSD_DIRECTORY + '/tmp/interpreter.txt'
TEMPLATES_DIRECTORY = '/templates'
 
# Memory constants
MAX_MODEL_RAM_USAGE = 3_500_000 # Size in bytes
 
# Web service constants
IMAGES_ON_PAGE = 9
 
# Model upload constants
BUFFER_SIZE = 100_000
MODEL_REQUEST_END_LENGTH = 46
FILE_STREAM_SPLITTER = b'application/octet-stream\r\n\r\n'
TEXT_SPLITTER = b'text/plain\r\n\r\n'
BYTE_CONTENT_END_SPLITTER = b'\r\n------'
 
# Device constants
PEER_MAC_ADDRESS = b'\xec\x62\x60\x9c\xfe\x4c'
 