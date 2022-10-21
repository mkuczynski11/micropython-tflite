from utils import get_file_size
import microlite
import sys
from config import TMP_INTERPRETER_LOG_PATH

def validate_required_memory(model_width, model_height):
    # Memory left for arena size = max_usage - (model_size + image input size)
    arena_size_memory = 100_000

    model = bytearray(get_file_size('sd/models/muschrooms/model.tflite'))
    file = open('sd/models/muschrooms/model.tflite', 'rb')
    file.readinto(model)
    file.close()

    interpreter = microlite.interpreter(model, arena_size_memory, None, None)
        
validate_required_memory(224, 224)