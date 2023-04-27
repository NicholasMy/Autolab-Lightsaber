import asyncio
import json
from typing import Optional, Awaitable

import tornado.web
import tornado.websocket
import tornado.ioloop

import secret
import config
from TangoConnection import TangoConnection
from LedStrip import LedStrip


class LightsaberWebSocket(tornado.websocket.WebSocketHandler):
    # Based on the tutorial here https://www.georgeho.org/tornado-websockets/
    clients = set()

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def open(self):
        LightsaberWebSocket.clients.add(self)
        self.send_entire_state()

    def on_message(self, message):
        pass

    def on_close(self):
        LightsaberWebSocket.clients.remove(self)

    @classmethod
    def broadcast(cls, message: str):
        for client in cls.clients:
            client.write_message(message)

    def check_origin(self, origin: str) -> bool:
        # This would be considered insecure on a website, but this is fine for our microcontroller
        # Besides, Nginx can add the correct headers anyway
        return True

    def send_entire_state(self):
        # Called on initial connection
        self.write_message(json.dumps(lightsaber.to_dict()))

    @staticmethod
    def send_updated_state(update_map: dict):
        # Called when the light needs to update
        LightsaberWebSocket.broadcast(json.dumps(update_map))


class MainHandler(tornado.web.RequestHandler):

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get(self):
        self.render("index.html")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", LightsaberWebSocket),
    ])


lightsaber = LedStrip(config.MAX_LED_INDEX, config.DEFAULT_LED_BRIGHTNESS)


def update_sender():
    old_lightsaber = lightsaber.copy()
    tango = TangoConnection(secret.TANGO_URL, secret.TANGO_KEY)
    jobs = tango.get_current_jobs_count()
    color = []
    if jobs == 0:
        lightsaber.clear_leds()
        lightsaber.fill_range(0, 5, [0, 255, 0])
    # Make the lightsaber more red as the number of jobs increases
    elif jobs == 1:
        color = [0, 0, 255]
    elif jobs == 2:
        color = [100, 0, 200]
    elif jobs == 3:
        color = [150, 0, 150]
    elif jobs == 4:
        color = [200, 0, 100]
    elif jobs >= 5:
        color = [255, 0, 0]

    if jobs != 0:
        lightsaber.fill_percent(jobs * 100 // 5, color)

    difference = lightsaber.get_difference_map(old_lightsaber)
    LightsaberWebSocket.send_updated_state(difference)
    print(str(lightsaber))


async def main():
    app = make_app()
    app.listen(6333)

    background_sender = tornado.ioloop.PeriodicCallback(update_sender, 1000 * config.TANGO_POLLING_INTERVAL)
    background_sender.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
