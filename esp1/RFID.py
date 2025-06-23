from time import sleep_ms
from machine import Pin, SPI
from mfrc522 import MFRC522

class RFID:
    def __init__(self, wsClient):
        self.sck = Pin(18, Pin.OUT)
        self.mosi = Pin(23, Pin.OUT)
        self.miso = Pin(19, Pin.OUT)
        self.spi = SPI(baudrate=100000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
        
        self.sda_pins = [
            {"pin": Pin(5, Pin.OUT), "region": "ile-de-france"},
            {"pin": Pin(17, Pin.OUT), "region": "auvergne-rhone-alpes"},
        ]
        
        self.buttons = [
            {"year": "1930", "pin": Pin(25, Pin.IN, Pin.PULL_UP), "pressed": False},
            {"year": "1950", "pin": Pin(14, Pin.IN, Pin.PULL_UP), "pressed": False},
            {"year": "1970", "pin": Pin(26, Pin.IN, Pin.PULL_UP), "pressed": False},
            {"year": "1990", "pin": Pin(32, Pin.IN, Pin.PULL_UP), "pressed": False},
            {"year": "2020", "pin": Pin(33, Pin.IN, Pin.PULL_UP), "pressed": False},
        ]
        
        self.tag_states = {reader["region"]: False for reader in self.sda_pins}
        self.wsClient = wsClient
        self.sendToESP = True
        self.mode = "rfid"
        self.year = ""

    def check_reader(self, cs_pin, region_name):
        for reader in self.sda_pins:
            reader["pin"].value(1)
        cs_pin.value(0)
        sleep_ms(50)

        reader = MFRC522(self.spi, cs_pin)
        (stat, tag_type) = reader.request(reader.REQIDL)

        if stat == reader.OK:
            (stat, raw_uid) = reader.anticoll()
            if stat == reader.OK:
                if not self.tag_states[region_name]:
                    # New tag just placed — send it
                    uid = "0x%02x%02x%02x%02x" % tuple(raw_uid[:4])
                    print(f"UID {uid} detected on {region_name}")
                    self.wsClient.send("HTMLPage", region_name, "")
                    self.tag_states[region_name] = True
                return True

        if self.tag_states[region_name]:
            self.tag_states[region_name] = False

        return False

    def check_buttons(self):
        for btn in self.buttons:
            if not btn["pin"].value() and not btn["pressed"]:
                btn["pressed"] = True
                return btn["year"]
            elif btn["pin"].value():
                btn["pressed"] = False
        return None
    
    def poll_buttons(self):
        year_pressed = self.check_buttons()
        if year_pressed:
            print(f"Detected button: {year_pressed}")
            self.wsClient.send("HTMLPage", "", year_pressed)

    def poll_rfid(self):
        self.sendToESP = True
        for reader in self.sda_pins:
            if self.check_reader(reader["pin"], reader["region"]):
                self.sendToESP = True
                return True

        if self.sendToESP:
            print("No RFID detected. Notifying ESP32-2 and ESP32-3.")
            self.wsClient.send("ESP32-2", "Unknown Region", "")
            self.wsClient.send("ESP32-3", "Unknown Region", "")
            self.poll_rfid()
           
        return False
