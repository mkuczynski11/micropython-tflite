import network
ssid = 'PowerLex-2.4'
password = '060900Power-Lex'

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(ssid, password)

# Then run
#
# import upip
# upip.install('picoweb')
# upip.install('micropython-ulogging') # TODO:REMOVE
# upip.install('ujson')
