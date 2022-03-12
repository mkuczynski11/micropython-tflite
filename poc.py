import numpy as np
import tensorflow as tf
import cv2

# Loading model
interpreter = tf.lite.Interpreter(model_path="mushroom.tflite")
interpreter.allocate_tensors()

# Reading input/output info
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f'input details: {input_details}\n')
print(f'output details: {output_details}\n')

# Reading sample image
img = cv2.imread('grzyb.jpg')
print(f'img: {img.shape}, dtype={img.dtype}\n')
img = cv2.resize(img, (360, 360))
images = img.reshape((1, img.shape[0], img.shape[1], img.shape[2])).astype(np.uint8)  # A batch of images with shape [batch_size, height, width, 3].
print(f'images: shape={images.shape}, dtype={images.dtype}\n')

# Saving image as the input for the model
interpreter.set_tensor(input_details[0]['index'], images)

# Inference
interpreter.invoke()

# Reading the output from inference
output_data = interpreter.get_tensor(output_details[0]['index'])
print(f'output_data: shape={output_data.shape} dtype={output_data.dtype}')

# Postprocessing
arg_max = np.argmax(output_data)
print(f'index={arg_max}, value={output_data[0][arg_max]}')
