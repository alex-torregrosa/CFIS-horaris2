""""Consumers for timetable generation"""
from channels.generic.websocket import JsonWebsocketConsumer
from horaris import generator


class GenerationConsumer(JsonWebsocketConsumer):
    """ Main timetable generation consumer"""

    def connect(self):
        # Called on connection. Either call
        print("Incoming socket, accepting", flush=True)
        self.accept()
        # Or to reject the connection, call
        # self.close()

    def receive_json(self, content):
        # Called with either text_data or bytes_data for each frame
        print("ws msg:", content)
        generator.send_progress(self, "Procesando datos...", 0)
        generator.calcula_horari(content, self)
        # You can call:
        #self.send(text_data="Hello world!")
        # Or, to send a binary frame:
        #self.send(bytes_data="Hello world!")
        # Want to force-close the connection? Call:
        # self.close()
        # Or add a custom WebSocket error code!
        # self.close(code=4123)

    def disconnect(self, close_code):
        # Called when the socket close
        print("Websocket connection closed")
