import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import cv2

# Loading model
model = hub.load("https://tfhub.dev/bohemian-visual-recognition-alliance/models/mushroom-identification_v1/2")

@tf.function(input_signature=[tf.TensorSpec(shape=[None, None, None, 3], dtype=tf.float32)])
def call_model(image_tensor):
  output_dict = model.signatures["serving_default"](image_tensor)
  return output_dict['out']
 
# Reading image
img = cv2.imread('grzyb.jpg')
print(f'img: {img.shape}, dtype={img.dtype}\n')
img = cv2.resize(img, (360, 360))
images = img.reshape((1, img.shape[0], img.shape[1], img.shape[2]))  # A batch of images with shape [batch_size, height, width, 3].
print(f'images: {images.shape}, dtype={images.dtype}\n')

# Inference and output reading
output_dict = call_model(images)  # Output dictionary.

# Postprocessing
output_dict = output_dict.numpy()
print(f'output_dict: {output_dict.shape}, output_dict={img.dtype}\n')
arg_max = np.argmax(output_dict)
print(f'index={arg_max}, value={output_dict[0][arg_max]}')
