
import uwebsockets.client
import uasyncio
import json

class WebSocketClient:
    
    def __init__(self, srcName, ip, port):
        self.uri = f"ws://{ip}:{port}"
        self.websocket = uwebsockets.client.connect(self.uri)
        self.srcName = srcName
        self.send_presentation_message()
        
    def send_presentation_message(self):
        presentation_message = {
            "client_name": self.srcName
        }
        self.websocket.send(json.dumps(presentation_message))
        print(f"Message de présentation envoyé: {presentation_message}")

    def send(self, dest, region, year):
        self.websocket.send(self.generate_json(self.srcName, dest, region, year))
        
    def generate_json(self, src, dest, region, year):
        return json.dumps({
            "src": src,
            "dest": dest,
            "region": region,
            "year": year
        })
    
    def receive(self):
        try:
            message = self.websocket.recv()
            print(f"Message reçu: {message}")
            return message
        except Exception as e:
            print(f"Erreur de réception: {e}")
            return None


