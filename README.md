# ESP32-CAM mushroom recognition
## Project dependencies
- [TFT screen driver](https://github.com/russhughes/st7789_mpy)
- [Camera driver](https://github.com/lemariva/micropython-camera-driver)
- [Espressif IoT Development Framework](https://github.com/espressif/esp-idf) - release v4.2
- [Micropython](https://github.com/micropython/micropython)
- [ESP32-camera](https://github.com/espressif/esp32-camera) - [`093688e`](https://github.com/espressif/esp32-camera/commit/093688e0b3521ac982bc3d38bbf92059d97e3613)

## DIY
```bash
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
git clone --recursive https://github.com/micropython/micropython.git
git clone https://github.com/lemariva/micropython-camera-driver.git
git clone https://github.com/russhughes/st7789_mpy.git
cd esp-idf/components
git clone https://github.com/espressif/esp32-camera
cd esp32-camera
git checkout 093688e
cd ../../../micropython
cp -r ../micropython-camera-driver/boards/ESP32_CAM/ ports/esp32/boards/ESP32_CAM
cd mpy-cross/
make
cd ../../esp-idf
./install.sh
. ./export.sh
cd ../micropython/ports/esp32/
make USER_C_MODULES=`full_path_to_cloned_repo`/micropython.cmake BOARD=ESP32_CAM
```

Successful build should generate `build-ESP32_CAM`in `micropython/ports/esp32` directory. Inside of it you can find firmware.bin which should contain all dependencies and after flashing it onto device you should be able to import `camera` and `st7789` libraries. 

*NOTE: This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.*
