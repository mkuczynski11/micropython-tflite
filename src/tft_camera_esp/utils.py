import os
import uos

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

def file_to_bytes(path):
    """
    Given path to file read its content and return it as bytes
    
    :return: bytes
    """
    with open(path, "rb") as f:
        return f.read()

def join_paths(*paths):
    """
    Join multiple paths into one
    
    :return: joined path
    """
    return "/".join(paths)

# Utility function to copy file from flash to sd card
# 
# BUFFER_SIZE = 100
# 
# def copy_file(src_filename, dst_filename):
#     """
#     Copy a file from one place to another. Both the source and destination
#     files must exist on the same machine.
#     
#     :param src_filename: str object pointing file to be copied
#     :param dst_filename: str object pointing where to copy source file
#     """
#     try:
#         with open(src_filename, 'rb') as src_file:
#             with open(dst_filename, 'wb') as dst_file:
#                 while True:
#                     buf = src_file.read(BUFFER_SIZE)
#                     if len(buf) > 0:
#                         dst_file.write(buf)
#                     if len(buf) < BUFFER_SIZE:
#                         break
#         return True
#     except:
#         return False
# 
# # copy_file('model.tflite', 'sd/model.tflite')


