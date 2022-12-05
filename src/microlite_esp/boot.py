# This file is executed on every boot (including wake-boot from deepsleep)
import uos
import machine
from config import (
    MICROSD_DIRECTORY,
    MODELS_PATH,
    IMAGES_PATH,
    TMP_IMAGE_PATH_DIR,
    TMP_MODEL_PATH_DIR,
    TEMPLATES_DIRECTORY
    )

try:
    sd = machine.SDCard(slot=3, width=1, sck=machine.Pin(14), mosi=machine.Pin(15), miso=machine.Pin(2), cs=machine.Pin(13))
    uos.mount(sd, MICROSD_DIRECTORY)
except Exception as e:
    machine.reset()

try:
    uos.mkdir(IMAGES_PATH)
except Exception as e:
    pass
    
try:
    uos.mkdir(MODELS_PATH)
except Exception as e:
    pass
    
try:
    uos.mkdir(TMP_IMAGE_PATH_DIR)
except Exception as e:
    pass
    
try:
    uos.mkdir(TMP_MODEL_PATH_DIR)
except Exception as e:
    pass
    
try:
    uos.mkdir(TEMPLATES_DIRECTORY)
except Exception as e:
    pass

