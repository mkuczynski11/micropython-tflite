# ESP32-CAM sources
## MicroSD card usage
In order to store larger data than few MB of data we are using MicroSD card. On each reset `boot.py` file is executed, therefore we have included card initializing and mounting inside of this file.

Base directory that MicroSD card is mounted to is `/sd`. In order to change it please check `config.py` file and change `directory` variable inside of `microsd_config`.
## Running prediction
### 1. Train and export model
This step is `optional`, however following it guarantees this example will work. If you do not want to train our own model you can skip this step, although we recommend it.

Take a look inside of [model training and exporting script](./big_schroom_model.ipynb) and open it in google collab. Then you need to simply run the script and let it finish, but before that there are some key adjustments to make:
- `batch_size` variable determines on what batch size train model on
- `img_height` varibale indicates height of input images of the network
- `img_width` varibale indicates width of input images of the network
- `cnn_feature_vector` variable points to already pretrained tensorflow hub cnn feature vector. It is possible to change current value to any other pretrained architecture, but the overall size, accuracy and latency of the network will differ.
- `quantization` variable is of type `str` and is either `none`, `dynamic`, `float` or `int`. It determines which type of quantization should be applied to model after traning during model exporting
- ```bash
    # Usage of google drive where we are storing our data
    from google.colab import drive
    drive.mount('/content/gdrive')

    data_dir = '/content/gdrive/MyDrive/Mushrooms' # directory of your data
    !rm -rf /content/gdrive/MyDrive/Mushrooms/.ipynb_checkpoints/
    ```
    This is configuration of where we store our data for training and validation. The dataset in our example is [muschroom dataset](https://www.kaggle.com/datasets/maysee/mushrooms-classification-common-genuss-images) from `kaggle` but `without Agaricus muschroom type`. This script requires access to google drive and the `data_dir` variable points to where our dataset has been saved on the google drive.

    We recommend to save the dataset on your google drive in the root directory(simply drop unpacked folder into the drive) and follow the script.

    *NOTE:* Script will ask you for permission to use your drive when the above code snippet runs. You can log into your google account where you stored the dataset and should be good to go.

With the above key adjustments in mind you can run the script and wait until it finishes. When everything is finished with success you simply need to download everything from the directory `tmp/models/{name_of_cnn_feature_vector}` where name_of_cnn_feature_vector in our example is `mobilenet_v1_025_224`. This directory contains:
- `{name_of_cnn_feature_vector}.tflite` file representing the model itself
- `labels.txt` file representing labels
- `{name_of_cnn_feature_vector}.txt` file which contains information about the model
- `maslak` file which is an image saved as bytes that has compatible shape to the model
### 2. Flashing source code onto esp32-cam
Inside this folder there are few files that our example requires to be flashed onto the device in order to run it.
This files are
- boot.py - operations that are run during device booting
- config.py - project configuration file
- model.py - classes responsible for model operations such as loading onto memory or prediction
- predict.py - example main function
- utils.py - utility functions  
Flash them into esp32-cam flash memory using `rshell` or any other software of your choice.  
TODO:Make guide to config.py  
*NOTE:* If you did not follow point 1 step then you will need to change some details in config.py file.
### 3. Exporting model into memory
If you have microsd card reader then simply copy the model that you downloaded early into sd card, but if that is not the case then we recommend flashing model into esp32-cam flash memory and copy it into microsd card memory using `copy_file` function from `utils.py` file. The file that represents our model should have `.tflite` extension and be named after cnn_feature_vector so in our example `mobilenet_v1_025_224.tflite`
### 4. Prepare an image
If you followed step 1 then you simply need to flash `maslak` file to the esp32-cam, but in other cases you need to flash any other image that meets such requirements:
- image has 3 color channels
- `img_width` is equal to on what the model was trained on
- `img_height` is equal to on what the model was trained on
- image is saved as a binary file
- image is not too big for the flash memory of esp32-cam module
### 5. Run the example
Assuming you have successfully completed all previous steps you can now run `predict.py` script and expect that your image will be classified.
