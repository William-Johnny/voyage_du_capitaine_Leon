from time import sleep_ms
from machine import Pin, SPI
from mfrc522 import MFRC522
from WSclient import WebSocketClient

class RFID:
    def __init__(self, wsClient):
        # SPI bus setup (shared)
        self.sck = Pin(18, Pin.OUT)
        self.mosi = Pin(23, Pin.OUT)
        self.miso = Pin(19, Pin.OUT)
        self.spi = SPI(baudrate=100000, polarity=0, phase=0, sck=self.sck, mosi=self.mosi, miso=self.miso)
        self.sda_pins = [
            (Pin(5, Pin.OUT), "centre-val-de-loire"),
            (Pin(22, Pin.OUT), "grand-est"),
            (Pin(17, Pin.OUT), "hauts-de-france"),
            (Pin(0, Pin.OUT), "occitanie"),
            (Pin(27, Pin.OUT), "normandie"),
            (Pin(16, Pin.OUT), "nouvelle-aquitaine"),
            (Pin(26, Pin.OUT), "provence-alpes-cote-d-azur"),
            (Pin(27, Pin.OUT), "bretagne")
        ]
        
        self.tag_states = {region_name: False for (_, region_name) in self.sda_pins}
        
        self.sendRfidData = True
        
        # Store year and WebSocket client
        self.wsClient = wsClient

    def check_reader(self, cs_pin, region_name):
    # Deselect all readers
        for (pin, _) in self.sda_pins:
            pin.value(1)
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
        else:
            # No tag currently present — reset state if it was previously detected
            if self.tag_states[region_name]:
                print(f"Tag removed from {region_name}")
                self.wsClient.send("ESP32-2", "Unknown Region", "")
                self.wsClient.send("ESP32-3", "Unknown Region", "")
            self.tag_states[region_name] = False

        return False


    def read(self):
        for (cs_pin, region_name) in self.sda_pins:
            if self.check_reader(cs_pin, region_name):
                return True
        return False
