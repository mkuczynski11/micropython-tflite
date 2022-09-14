# ESP32-CAM mushroom recognition
## Project dependencies
- [TFT screen driver](https://github.com/russhughes/st7789_mpy)
- [Camera driver](https://github.com/lemariva/micropython-camera-driver)
- [Espressif IoT Development Framework](https://github.com/espressif/esp-idf) - release v4.2
- [Micropython](https://github.com/micropython/micropython)
- [ESP32-camera](https://github.com/espressif/esp32-camera) - [`093688e`](https://github.com/espressif/esp32-camera/commit/093688e0b3521ac982bc3d38bbf92059d97e3613)

## ESP32-CAM firmware building
You can access pre-build firmware in `firmware` directory of this repo, however below are listed steps required to generate it by yourself.
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
cp ../../../st7789_mpy/fonts/bitmap/vga1_16x16.py modules # Optional: Adding font in order to display text
make USER_C_MODULES=`full_path_to_cloned_repo`/micropython.cmake BOARD=ESP32_CAM FROZEN_MANIFEST="" FROZEN_MPY_DIR=$UPYDIR/modules
```

Successful build should generate `build-ESP32_CAM`in `micropython/ports/esp32` directory. Inside of it you can find firmware.bin which should contain all dependencies and after flashing it onto device you should be able to import `camera` and `st7789` libraries. 

*NOTE: This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.*

## ESP32 microlite firmware building
*NOTE: THIS STEPS ARE INITIAL AND WILL BE UPDATED LATER*
```bash
cd tensorflow-micropython-examples # clone of microlite repo
git submodule init
git submodule update --recursive
cd micropython
git submodule update --init lib/axtls
git submodule update --init lib/berkeley-db-1.xx
cd ..
rm -rf ./micropython-modules/microlite/tflm
cd ./tensorflow
../micropython-modules/microlite/prepare-tflm-esp.sh
cd ../..
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
./esp-idf/install.sh
. ./esp-idf/export.sh
cd tensorflow-micropython-examples/micropython
make -C mpy-cross V=1 clean all
cd ../boards/esp32/MICROLITE
rm -rf build
idf.py build
```

*NOTE: Use this command to flash firmware*
esptool.py -p COM3 -b 460800 --before default_reset --after hard_reset --chip esp32 write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 .\microlite\bootloader\bootloader.bin 0x8000 .\microlite\partition_table\partition-table.bin 0x10000 .\microlite\micropython.bin

## Building micropython with 16 MB memory
```bash
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
git clone --recursive https://github.com/micropython/micropython.git
cd micropython/mpy-cross/
make
cd ../../esp-idf
./install.sh
. ./export.sh
cd ../micropython/ports/esp32/
cp -r ../../../boards/fire_beetle/ ./boards/fire_beetle
make BOARD=fire_beetle
```

Successful build should generate `build-fire_beetle`in `micropython/ports/esp32` directory. Inside of it you can find firmware.bin which should contain all dependencies and after flashing it onto device you should have flash size of 16MB. 
