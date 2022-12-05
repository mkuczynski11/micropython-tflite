import network
try:
  import usocket as socket
except:
  import socket
    
class CredentialsService:
    def __init__(self, ssid, password, ap_if):
        self.ssid = ssid
        self.password = password
        self._ap_if = ap_if
        
    def start_ap(self):
        self._ap_if.active(True)
        self._ap_if.config(ssid=self.ssid, password=self.password)
        self._ap_if.config(authmode=3)
        
        while self._ap_if.active() == False:
            pass
        print('Access point setup complete')
    
    def stop_ap(self):
        self._ap_if.active(False)
        print('Access point shut down')
        
    def wait_for_credentials(self, port=80):
        soc = socket.socket()
        soc.bind(('',port))
        soc.listen(5)
        print("Listening on 192.168.4.1")
        while True:
            
            client, addr = soc.accept()
            print("Client connected from", addr)
            request = client.recv(1024)
            request = request.decode().split()

            ssid, password = '', ''

            if 'ssid' in request[1]:
                ssid = request[1].split('&')[0].split('=')[1]
                password = request[1].split('&')[1].split('=')[1]
                print(f'SSID = {ssid}, password = {password}')
                print("The SSID is", ssid, "and the Password is", password)
                client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
                client.send(self._get_success())
                client.close()
                
                return ssid, password
            print(request)

            client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
            client.send(self._get_form())
            client.close()
        
    def send_response(self, client, payload, status_code=200):
        client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
        client.sendall("Content-Type: text/html\r\n")
        client.sendall("Content-Length: {}\r\n".format(len(payload)))
        client.sendall("\r\n")

        if len(payload) > 0:
            client.sendall(payload)
        
    def _get_form(self):
        form = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>ESP8266 connection</title>
            </head>
            <body>
                <h2>
                    Enter the UID and Password to connect to WiFi
                </h2>
                <form action="/post">
                    uid: <input type="text" name="ssid">
                    password: <input type="text" name="password">
                    <input type="submit" value="Submit">
                </form><br>
            </body>
        </html>
        """
        return form
        
    def _get_success(self):
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>ESP8266 connection</title>
            </head>
            <body>
                <h2>
                    Success!
                </h2>
            </body>
        </html>
        """
        return html
        
        
    def get_credentials(self):
        pass



