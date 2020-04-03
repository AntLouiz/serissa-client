import threading
import websocket
import time
import json
from stream import stream_faces


class WebsocketStreamClient(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        super(WebsocketStreamClient, self).__init__(*args, **kwargs)
        self.stream_thread = threading.Thread(
            target=stream_faces,
            args=(self, )
        )
        self.on_open = self.open
        self.on_message = self.receive
        self.consumer = threading.Lock()
        self.producer = threading.Lock()

    def open(self, *args):
        print("Oppened")
        self.consumer.acquire()
        self.stream_thread.start()

    def receive(self, *args):
        self.consumer.acquire()
        data = json.loads(args[0])
        matrice = data['matrice']

        if matrice != 'unknown':
            print("Abrir porta para o usuario com a matricula: {}".format(
                matrice
            ))

        time.sleep(3)

        if matrice != 'unknown':
            print("Fechar porta")

        time.sleep(3)

        self.producer.release()


if __name__ == "__main__":
    websocket.enableTrace(True)
    port = 8000
    ws = WebsocketStreamClient('ws://localhost:{}'.format(port))
    ws.run_forever()
