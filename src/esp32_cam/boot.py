# This file is executed on every boot (including wake-boot from deepsleep)
try:
    import uos
    import machine
    from config import microsd_config
    
    sd = machine.SDCard(slot=3, width=1, sck=machine.Pin(14), mosi=machine.Pin(15), miso=machine.Pin(2), cs=machine.Pin(13))
    uos.mount(sd, microsd_config['directory'])
except Exception as e:
    print("Error ocurred: " + str(e))
    machine.reset()
    
