from websocket_server import WebsocketServer
from typing import Any, TypeVar, Type, cast
import json

T = TypeVar("T")

def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x

def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()

class PresentationMessage:
    client_name: str

    def __init__(self, client_name: str) -> None:
        self.client_name = client_name

    @staticmethod
    def from_dict(obj: Any) -> 'PresentationMessage':
        assert isinstance(obj, dict)
        client_name = from_str(obj.get("client_name"))
        return PresentationMessage(client_name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["client_name"] = from_str(self.client_name)
        return result
    
    
def presentation_message_from_dict(s: Any) -> PresentationMessage:
    return PresentationMessage.from_dict(s)


def presentation_message_to_dict(x: PresentationMessage) -> Any:
    return to_class(PresentationMessage, x)    



def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Message:
    src: str
    dest: str
    region: str
    year: str

    def __init__(self, src: str, dest: str, region: str, year: str) -> None:
        self.src = src
        self.dest = dest
        self.region = region
        self.year = year

    @staticmethod
    def from_dict(obj: Any) -> 'Message':
        assert isinstance(obj, dict)
        src = from_str(obj.get("src"))
        dest = from_str(obj.get("dest"))
        region = from_str(obj.get("region"))
        year = from_str(obj.get("year"))
        return Message(src, dest, region, year)

    def to_dict(self) -> dict:
        result: dict = {}
        result["src"] = from_str(self.src)
        result["dest"] = from_str(self.dest)
        result["region"] = from_str(self.region)
        result["year"] = from_str(self.year)
        return result


def message_from_dict(s: Any) -> Message:
    return Message.from_dict(s)


def message_to_dict(x: Message) -> Any:
    return to_class(Message, x)

class WSServer:
    
    def __init__(self, port, url):
        # Création du serveur WebSocket
        self.PORT = port
        self.server = WebsocketServer(host=url, port=self.PORT)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)   
        self.client_dict = {}
        self.client_obj_dict = {}

    # Fonction appelée lorsqu'un nouveau client se connecte
    def new_client(self,client, server):
        print(f"Nouveau client connecté: {client['id']}")
        #server.send_message_to_all(f"Client {client['id']} connecté.")

    # Fonction appelée lorsqu'un client envoie un message
    def message_received(self,client, server, message):
        print(f"Message reçu de {client['id']}: {message}")
        
        # si l'id du client n'existe pas dans le dictionnaire, on l'ajoute
        if self.client_dict.get(client['id']) is None:
            obj = presentation_message_from_dict(json.loads(message))
            self.client_dict[client['id']] = obj.client_name
            self.client_obj_dict[client['id']] = client
            #self.server.send_message(client,f"PRESENTATION_OK")
        else:
            obj = message_from_dict(json.loads(message))
            print(f"Message reçu de {self.client_dict[client['id']]} pour {obj.dest} : {obj.region} {obj.year}")
            
            if self.client_exists(obj.dest) == False:
                #self.server.send_message(client,f"DEST_UNAVAILABLE")
                print("DEST_UNAVAILABLE")
            else:
                dest_client = self.client_obj_dict[self.get_client_from_name(obj.dest)]
                self.server.send_message(dest_client,message)
                print(obj.region)
                if obj.region != "Unknown Region":
                    print("ok")
                    esp_client = self.client_obj_dict[self.get_client_from_name("ESP32")]
                    self.server.send_message(esp_client, json.dumps({"rfid": obj.region}))
                
    def get_client_from_name(self, name):
        for key in self.client_dict:
            if self.client_dict[key] == name:
                return key        
            
    def client_exists(self,dest):
        dest_exists = False
        for key in self.client_dict:
            if self.client_dict[key] == dest:
                dest_exists = True
                break
        return dest_exists
            
    # Fonction appelée lorsqu'un client se déconnecte
    def client_left(self, client, server):
        print(f"Client {client['id']} déconnecté")
        server.send_message_to_all(f"Client {client['id']} déconnecté.")

    # Fonction pour démarrer le serveur
    def start(self):
        print(f"Serveur WebSocket démarré sur le port {self.PORT}")
        self.server.run_forever()


wsServer = WSServer(8080, "192.168.10.140")
#wsServer = WSServer(8080, "localhost")
wsServer.start()
