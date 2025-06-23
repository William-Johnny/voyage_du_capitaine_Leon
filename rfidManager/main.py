import time
import json
from RFID import *
from WSclient import WebSocketClient

ws = WebSocketClient("ESP32", "192.168.10.140", 8080)
rfid = RFID(ws)

unknown_region_sent = False
last_rfid_check = time.ticks_ms()
found_tag = ""

while True:
    now = time.ticks_ms()

    if time.ticks_diff(now, last_rfid_check) > 200:
        if rfid.mode == "rfid":
            # Always check for RFID tag
            rfid_tag = rfid.poll_rfid()
            last_rfid_check = time.ticks_ms()

            # Also always check for server message
            msg = ws.receive()
            if msg:
                try:
                    data = json.loads(msg)
                    if "rfid" in data and data["rfid"]:
                        print(f"Using RFID from server: {data['rfid']}")
                        rfid.current_rfid_from_server = data['rfid']
                        found_tag = data['rfid']
                except Exception as e:
                    print("Error decoding message:", e)

            if rfid_tag:
                found_tag = rfid_tag

            if found_tag:
                rfid.mode = "buttons"
                unknown_region_sent = False
            else:
                if not unknown_region_sent:
                    print("No RFID detected. Notifying ESP32-2 and ESP32-3.")
                    ws.send("ESP32-2", "Unknown Region", "")
                    ws.send("ESP32-3", "Unknown Region", "")
                    unknown_region_sent = True

        elif rfid.mode == "buttons":
            # Poll buttons continuously
            button_pressed = rfid.poll_buttons()
            # If you ever want to switch back to RFID mode after a timeout or event, do it here

    time.sleep(0.01)
