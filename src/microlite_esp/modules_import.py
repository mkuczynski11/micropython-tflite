import network
ssid = 'UPC240648036'
password = '6SSGYAWT'

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)

# Then run
#
import upip
upip.install('picoweb')
upip.install('micropython-ulogging') # TODO:REMOVE
upip.install('ujson')
