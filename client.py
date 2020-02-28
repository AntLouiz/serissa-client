import threading
import websocket
import time
from cache import redis_instance
from stream import stream_faces


class WebsocketStreamClient(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def receive(self, *args):
        redis_instance.set('flag', 0)
        time.sleep(3)
        redis_instance.set('flag', 1)


if __name__ == "__main__":
    websocket.enableTrace(True)
    port = 8000
    ws = WebsocketStreamClient('ws://localhost:{}'.format(port))
    ws.run_forever()
