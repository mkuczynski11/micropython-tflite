# ESP32-CAM mushroom recognition
## Project dependencies
- [TFT screen driver](https://github.com/russhughes/st7789_mpy)
- [Camera driver](https://github.com/lemariva/micropython-camera-driver)
- [Espressif IoT Development Framework](https://github.com/espressif/esp-idf) - [`b64925c56`](https://github.com/espressif/esp-idf/commit/b64925c5673206100eaf4337d064d0fe3507eaec)
- [Micropython](https://github.com/micropython/micropython) - [`feeeb5ea3`](https://github.com/micropython/micropython/commit/feeeb5ea3afe801b381eb5d4b310e83290634c46)
- [ESP32-camera](https://github.com/espressif/esp32-camera) - [`093688e`](https://github.com/espressif/esp32-camera/commit/093688e0b3521ac982bc3d38bbf92059d97e3613)

## Build firmware
```bash
cd esp-idf
./install.sh
. ./export.sh
cd ../micropython/ports/esp32
make USER_C_MODULES=`full_path_to_cloned_repo`/modules/micropython.cmake BOARD=ESP32_CAM
```

*NOTE: This guide is made for ESP32-CAM AI-THINKER module. Trying to build firmware intended for other modules should work provided following the correct [micropython](https://github.com/micropython/micropython) guide.*
