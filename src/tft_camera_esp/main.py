import camera
from machine import Pin, SPI
import st7789

mosi = 13
sck = 14
cs = 15
dc = 2
rst = 12
baud = 31250000


def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=31250000, sck=Pin(sck), mosi=Pin(mosi)),
        240,
        240,
        reset=Pin(rst, Pin.OUT),
        cs=Pin(cs, Pin.OUT),
        dc=Pin(dc, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)

def main():
    camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
    camera.framesize(camera.FRAME_240X240)
    
    tft = config(0)
    tft.init()
    tft.fill(st7789.BLUE)
#     tft.rotation(2)
    
    while True:
        buf = camera.capture()
        
        tft.jpg_from_buffer(buf, 0, 0)
        
        
    camera.deinit()

main()
