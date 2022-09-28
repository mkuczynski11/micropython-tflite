# ESP32-CAM mushroom recognition
## Project dependencies
- [TFT screen driver](https://github.com/russhughes/st7789_mpy)
- [Camera driver](https://github.com/lemariva/micropython-camera-driver)
- [Espressif IoT Development Framework](https://github.com/espressif/esp-idf) - release v4.2
- [Micropython](https://github.com/micropython/micropython)
- [ESP32-camera](https://github.com/espressif/esp32-camera) - [`093688e`](https://github.com/espressif/esp32-camera/commit/093688e0b3521ac982bc3d38bbf92059d97e3613)
- [Microlite](https://github.com/mocleiri/tensorflow-micropython-examples)

## ESP32_CAM with camera driver and microlite building
You can access pre-build firmware in `firmware` directory of this repo, however below are listed steps required to generate it by yourself.
```bash
pip install Pillow
pip install Wave
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
. ./export.sh
git clone https://github.com/mocleiri/tensorflow-micropython-examples.git
cd tensorflow-micropython-examples
git submodule init
git submodule update --recursive
cd micropython
git submodule update --init lib/axtls
git submodule update --init lib/berkeley-db-1.xx
cd ..
rm -rf ./micropython-modules/microlite/tflm
cd tensorflow
../micropython-modules/microlite/prepare-tflm-esp.sh
cd ../micropython
make -C mpy-cross V=1 clean all
cd ../tflm_esp_kernels
git submodule update --init
git submodule update --recursive
cd ../boards/esp32/MICROLITE_SPIRAM_CAM
rm -rf build
idf.py build
```

Successful build should generate `build-ESP32_CAM`in `micropython/ports/esp32` directory. Inside of it you can find micropython.bin, bootloader dir and partition_table dir which should contain all dependencies and after flashing it onto device you should be able to import `camera` and `microlite` libraries. 

*NOTE:* This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.

*NOTE:* Use this command to flash firmware
```bash
esptool.py -p COM3 -b 460800 --before default_reset --after hard_reset --chip esp32 write_flash --flash_mode dio --flash_size detect --flash_freq 40m 0x1000 .\bootloader\bootloader.bin 0x8000 .\partition_table\partition-table.bin 0x10000 .\micropython.bin
```

## Fire_beetle esp32 with st7789 building
You can access pre-build firmware in `firmware` directory of this repo, however below are listed steps required to generate it by yourself.
```bash
git clone -b v4.2 --recursive https://github.com/espressif/esp-idf.git
git clone --recursive https://github.com/micropython/micropython.git
git clone https://github.com/russhughes/st7789_mpy.git
cd micropython/mpy-cross/
make
cd ../../esp-idf
./install.sh
. ./export.sh
cd ../micropython/ports/esp32/
cp -r ../../../boards/fire_beetle/ ./boards/fire_beetle
cp ../../../st7789_mpy/fonts/bitmap/vga1_16x16.py modules # Optional: Adding font in order to display text
make USER_C_MODULES=`full_path_to_cloned_repo`/micropython.cmake BOARD=fire_beetle FROZEN_MANIFEST="" FROZEN_MPY_DIR=$UPYDIR/modules
```

Successful build should generate `build-fire_beetle`in `micropython/ports/esp32` directory. Inside of it you can find firmware.bin which should contain all dependencies and after flashing it onto device you should have flash size of 16MB and `st7789` library. 

*NOTE:* This guide is made for ESP32 Fire_beetle module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.
