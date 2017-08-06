from channels.routing import route
from time import sleep;
import horaris.generator as generator
import json

def ws_conn(message):
    # Accepta la conexió del websocket
    message.reply_channel.send({"accept": True})
    # message.reply_channel.send({"text": "hola"})


def ws_message(message):
    # Calcula l'horari amb les dades rebudes
    print("ws msg",message["text"])
    generator.sendProgress(message,"Procesando datos...",0)
    asigs = json.loads(message["text"])
    generator.calculaHorari(asigs,message)

channel_routing = [
route('websocket.connect',ws_conn),
route("websocket.receive", ws_message),
]
