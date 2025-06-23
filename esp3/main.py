import uwebsockets.client
import _thread
import time
from WSclient import WebSocketClient

from RFID import *

rfid = None

import json

def start_ws():
    global rfid
    try:
        wsClient = WebSocketClient("ESP32-2", "192.168.10.140", "8080")
        print("WebSocket connected")

        while True:
            msg = wsClient.receive()

            # Only try to parse if message looks like JSON
            if msg.strip().startswith("{") and msg.strip().endswith("}"):
                try:
                    data = json.loads(msg)
                    print(data)
                    if rfid is None and "region" in data and data["region"] == "Unknown Region":
                        rfid = RFID(wsClient)
                except Exception as e:
                    print("JSON parse error:", e)
                    return
            else:
                print("Non-JSON message received:", msg)

            time.sleep(0.1)
    except Exception as e:
        print("WebSocket error:", e)

# Start WebSocket listener thread
_thread.start_new_thread(start_ws, ())

# Main loop
while True:
    if rfid:
        rfid.read()
    time.sleep(0.1)
