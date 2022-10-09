import camera
from machine import Pin, SPI
import st7789

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=31250000, sck=Pin(14), mosi=Pin(13)),
        240,
        240,
        reset=Pin(2, Pin.OUT),
        cs=Pin(15, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(1, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)

def main():
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
    camera.framesize(camera.FRAME_240X240)
    
    tft = config(0)
    tft.init()
    tft.rotation(2)
    
    while True:
        buf = camera.capture()
        f = open('pic.jpg', 'w')
        f.write(buf)
        f.close()
        
        tft.jpg('pic.jpg', 0, 0)
        
    camera.deinit()

main()


