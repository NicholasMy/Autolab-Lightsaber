import asyncio
import json
import random
from typing import Optional, Awaitable

import tornado.web
import tornado.websocket
import tornado.ioloop


class LightsaberWebSocket(tornado.websocket.WebSocketHandler):
    # Based on the tutorial here https://www.georgeho.org/tornado-websockets/
    clients = set()

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def open(self):
        LightsaberWebSocket.clients.add(self)
        print("WebSocket opened")
        self.send_entire_state()

    def on_message(self, message):
        print("Message received: " + message)

    def on_close(self):
        LightsaberWebSocket.clients.remove(self)
        print("WebSocket closed")

    @classmethod
    def broadcast(cls, message: str):
        for client in cls.clients:
            client.write_message(message)

    def check_origin(self, origin: str) -> bool:
        # This is insecure, but it's just for testing.
        return True

    def send_entire_state(self):
        # Called on initial connection
        print("Sending entire state")
        self.write_message(json.dumps(get_dummy_data()))

    @staticmethod
    def send_updated_state():
        # Called when the light needs to update
        # TODO this will actually be called when Autolab's stress level changes
        LightsaberWebSocket.broadcast(json.dumps(get_dummy_update()))


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", LightsaberWebSocket),
    ])


def get_dummy_data():
    return {
        "brightness": 5,
        0: [1, 2, 3],
        1: [4, 5, 6],
        2: [7, 8, 9],
        3: [10, 11, 12],
        4: [13, 14, 15],
        5: [16, 17, 18],
    }


def get_dummy_update():
    valid_leds = [0, 1, 2, 3, 4, 5]
    number_of_updates = random.randint(1, 3)
    leds_to_update = random.sample(valid_leds, number_of_updates)

    ret = {}

    for led in leds_to_update:
        vals = get_dummy_data()[led]
        ret[led] = [vals[0] + random.randint(1, 100), vals[1] + random.randint(1, 100),
                    vals[2] + random.randint(1, 100)]

    update_brightness = random.randint(0, 3)
    if update_brightness == 0:
        ret["brightness"] = random.randint(2, 10)

    return ret


def dummy_sender():
    LightsaberWebSocket.send_updated_state()


async def main():
    app = make_app()
    app.listen(6333)

    background_sender = tornado.ioloop.PeriodicCallback(dummy_sender, 1000)
    background_sender.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
