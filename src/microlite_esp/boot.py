# This file is executed on every boot (including wake-boot from deepsleep)
import uos
import machine
from config import (
    MICROSD_DIRECTORY,
    MODELS_PATH,
    IMAGES_PATH,
    TMP_IMAGE_PATH,
    TMP_MODEL_PATH
    )

try:
    sd = machine.SDCard(slot=3, width=1, sck=machine.Pin(14), mosi=machine.Pin(15), miso=machine.Pin(2), cs=machine.Pin(13))
    uos.mount(sd, MICROSD_DIRECTORY)
except Exception as e:
    print("Couldn't mount sd card")
    print("Error ocurred: " + str(e))
    machine.reset()

try:
    uos.mkdir(IMAGES_PATH)
except Exception as e:
    print("Couldn't create images directory")
    print("Error ocurred: " + str(e))
    
try:
    uos.mkdir(MODELS_PATH)
except Exception as e:
    print("Couldn't create models directory")
    print("Error ocurred: " + str(e))
    
try:
    uos.mkdir(TMP_IMAGE_PATH)
except Exception as e:
    print("Couldn't create tmp image directory")
    print("Error ocurred: " + str(e))
    
try:
    uos.mkdir(TMP_MODEL_PATH)
except Exception as e:
    print("Couldn't create tmp image directory")
    print("Error ocurred: " + str(e))
    
