# ESP32-CAM sources
## MicroSD card usage
In order to store larger data than few MB of data we are using MicroSD card. On each reset `boot.py` file is executed, therefore we have included card initializing and mounting inside of this file.

Base directory that MicroSD card is mounted to is `/sd`. In order to change it please check `config.py` file and change `directory` variable inside of `microsd_config`
.