import threading
import websocket
import time
import json
import RPi.GPIO as GPIO
from cache import redis_instance
from stream import stream_faces


CHANNEL = 21
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(CHANNEL, GPIO.OUT)


class WebsocketStreamClient(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        super(WebsocketStreamClient, self).__init__(*args, **kwargs)
        self.stream_thread = threading.Thread(
            target=stream_faces,
            args=(self, )
        )
        self.on_open = self.open
        self.on_message = self.receive

    def open(self, *args):
        print("Oppened")
        redis_instance.set('flag', 1)
        self.stream_thread.start()

    def open_door(self, pin):
        GPIO.output(pin, GPIO.HIGH)

    def close_door(self, pin):
        GPIO.output(pin, GPIO.LOW)

    def receive(self, *args):
        redis_instance.set('flag', 0)
        data = json.loads(args[0])
        matrice = data['matrice']

        if matrice != 'unknown':
            print("Abrir porta para o usuario com a matricula: {}".format(
                matrice
            ))
            self.open_door(CHANNEL)

        time.sleep(3)

        if matrice != 'unknown':
            print("Fechar porta")
            self.close_door(CHANNEL)

        time.sleep(3)

        redis_instance.set('flag', 1)


if __name__ == "__main__":
    websocket.enableTrace(True)
    host = 'localhost'
    port = 8000
    ws = WebsocketStreamClient('ws://{}:{}'.format(host, port))
    ws.run_forever()
    GPIO.cleanup()
