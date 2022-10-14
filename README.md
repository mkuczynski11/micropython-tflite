# ESP32-CAM mushroom recognition
## Project dependencies
### Fire_beetle
- [TFT screen driver](https://github.com/russhughes/st7789_mpy)
- [Espressif IoT Development Framework](https://github.com/espressif/esp-idf) - release v4.2 or v4.3.1
- [Micropython](https://github.com/micropython/micropython)
- [Microlite](https://github.com/mocleiri/tensorflow-micropython-examples)
- [Camera driver](https://github.com/lemariva/micropython-camera-driver)

## Firmware with microlite building
You can access pre-build firmware in `firmware` directory of this repo, however below are listed steps required to generate it by yourself.
```bash
# Setup esp-idf
git clone -b v4.3.1 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
. ./export.sh
# Install pip dependencies
. /home/mkuczyns/.espressif/python_env/idf4.3_py3.8_env/bin/activate
pip install Pillow
pip install Wave
# Clone and update microlite repo
cd ..
git clone https://github.com/mocleiri/tensorflow-micropython-examples.git
cd tensorflow-micropython-examples
git submodule init
git submodule update --recursive
# Clone the newest micropython and update required submodules
rm -rf micropython
git clone https://github.com/glenn20/micropython.git
cd micropython
git checkout 5a8312f15c5a5fcc776f3710efca3bf017607170
git submodule update --init lib/axtls
git submodule update --init lib/berkeley-db-1.xx
# Prepare microlite
rm -rf ../micropython-modules/microlite/tflm
cd ../tensorflow
../micropython-modules/microlite/prepare-tflm-esp.sh
# Initialize camera drivers
cd ../tflm_esp_kernels
git submodule update --init examples/person_detection/esp32-camera
# Prepare for build
cd ../micropython/mpy-cross
. ../../../esp-idf/export.sh 
make
# Replace microlite and camera driver source code to the latest micropython requirements
cd ../../..
rm -rf tensorflow-micropython-examples/micropython-modules/microlite/tensorflow-microlite.c
rm -rf tensorflow-micropython-examples/micropython-modules/micropython-camera-driver/modcamera.c
rm -rf tensorflow-micropython-examples/micropython-modules/micropython.cmake
cp boards/tft_camera/modcamera.c tensorflow-micropython-examples/micropython-modules/micropython-camera-driver/
cp boards/microlite/tensorflow-microlite.c tensorflow-micropython-examples/micropython-modules/microlite/
cp boards/microlite/micropython.cmake tensorflow-micropython-examples/micropython-modules/micropython.cmake
cp -r boards/microlite/jpglib tensorflow-micropython-examples/micropython-modules/jpglib
# Checkout to the updated ulab version
cd tensorflow-micropython-examples
rm -rf micropython-ulab
git clone https://github.com/v923z/micropython-ulab.git
cd micropython-ulab
git checkout 5ccfa5cdd9040c2c4219c07b005256427d31ed1c
# Build firmware
. ../../esp-idf/export.sh
cd ../micropython/ports/esp32
make BOARD= submodules
cd ../../../boards/esp32/MICROLITE_SPIRAM
rm -rf build
idf.py build
```

Successful build should generate `build`in `tensorflow-micropython-examples/boards/esp32/MICROLITE_SPIRAM` directory. Inside of it you can find micropython.bin, bootloader dir and partition_table dir which should contain all dependencies and after flashing it onto device you should be able to import `microlite` library. 

*NOTE:* This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.

*NOTE:* Use this command to flash firmware
```bash
esptool.py -p COM3 -b 460800 --before default_reset --after hard_reset --chip esp32 write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 .\bootloader\bootloader.bin 0x8000 .\partition_table\partition-table.bin 0x10000 .\micropython.bin
```

## Firmware with st7789 and camera driver building
You can access pre-build firmware in `firmware` directory of this repo, however below are listed steps required to generate it by yourself.
```bash
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
git clone --recursive https://github.com/glenn20/micropython.git
git clone https://github.com/russhughes/st7789_mpy.git
git clone https://github.com/lemariva/micropython-camera-driver
rm micropython-camera-driver/src/modcamera.c
rm st7789_mpy/st7789/st7789.c
cp boards/tft_camera/modcamera.c micropython-camera-driver/src/modcamera.c
cp boards/tft_camera/st7789.c st7789_mpy/st7789/st7789.c
cd esp-idf/components
git clone https://github.com/espressif/esp32-camera
cd esp32-camera
git checkout 093688e0b3521ac982bc3d38bbf92059d97e3613
cd ../../../esp-idf
./install.sh
. ./export.sh
cd ../micropython/mpy-cross/
git checkout 5a8312f15c5a5fcc776f3710efca3bf017607170
make
cd ../ports/esp32/
cp -r ../../../micropython-camera-driver/boards/ESP32_CAM/ ./boards/ESP32_CAM
cp ../../../st7789_mpy/fonts/bitmap/vga1_16x16.py modules # Optional: Adding font in order to display text
make USER_C_MODULES=`full_path_to_cloned_repo`/micropython.cmake BOARD=ESP32_CAM FROZEN_MANIFEST="" FROZEN_MPY_DIR=$UPYDIR/modules
```

Successful build should generate `build-ESP32_CAM`in `micropython/ports/esp32` directory. Inside of it you can find firmware.bin which should contain all dependencies and after flashing it onto device you should have `st7789` AND `camera` libraries. 

*NOTE:* This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.
