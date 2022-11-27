import os
import uos
import gc

class ResponseCode:
    OK = "OK"
    NOT_ENOUGH_MEMORY = "SD card has reached its maximum memory"
    MODEL_NOT_FOUND = "model was not found"
    CLASS_NOT_FOUND = "class was not found"
    IMAGE_NOT_FOUND = "image was not found"

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

def get_file_size(path):
    """
    Given path to file determine its size in bytes
    
    :return: file size in bytes
    """
    return os.stat(path)[6]

def get_free_space(path):
    stats = uos.statvfs(path)
    return stats[1]*stats[3]

def dims_to_size(dims):
    """
    Given array or tuple of dimensions determine the overall size
    
    :return: overall size of array or tuple
    """
    size = 1
    for dim in dims:
        size *= dim
    return size
