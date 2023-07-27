import asyncio
import datetime
import json
import random
from typing import Optional, Awaitable

import tornado.web
import tornado.websocket
import tornado.ioloop

import config
from AnimatedLedStrip import AnimatedLedStrip
from color_map_builder import build_linear_color_map


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
        self.write_message(json.dumps(lightsaber.led_strip.to_dict()))

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


lightsaber = AnimatedLedStrip(config.MAX_LED_INDEX, config.DEFAULT_LED_BRIGHTNESS)
old_lightsaber = lightsaber.led_strip.copy()
last_update_time = datetime.datetime.now()
ANIMATION_DURATION_SECS = 2.5
DATA_FETCH_SECS = 1.0
WS_SEND_FREQUENCY_SECS = 0.03


def update_target():
    # portal = AutolabPortalConnection(secret.PORTAL_URL, secret.PORTAL_API_KEY)
    # jobs = portal.get_tango_histogram()[86400]
    # jobs = random.randint(0, 5)
    # target_percent = jobs * 100 // 5
    target_length = random.randint(0, config.MAX_LED_INDEX)
    # Just for testing; this is very inefficient:
    color_map = random.choice([
        build_linear_color_map([0, 0, 255], [255, 0, 0], config.MAX_LED_INDEX),
        build_linear_color_map([255, 0, 0], [0, 0, 255], config.MAX_LED_INDEX),
        build_linear_color_map([0, 255, 0], [255, 0, 0], config.MAX_LED_INDEX),
        build_linear_color_map([255, 0, 0], [0, 255, 0], config.MAX_LED_INDEX),
        build_linear_color_map([0, 255, 0], [0, 0, 255], config.MAX_LED_INDEX),
        build_linear_color_map([0, 0, 255], [0, 255, 0], config.MAX_LED_INDEX),
    ])
    lightsaber.set_target_state(target_length, color_map, random.random() * ANIMATION_DURATION_SECS + 0.5)


def update_sender():
    global lightsaber, old_lightsaber, last_update_time

    now = datetime.datetime.now()
    if now - last_update_time > datetime.timedelta(seconds=DATA_FETCH_SECS):
        update_target()
        last_update_time = now

    new_lightsaber = lightsaber.led_strip.copy()

    difference = new_lightsaber.get_difference_map(old_lightsaber)
    LightsaberWebSocket.send_updated_state(difference)
    old_lightsaber = new_lightsaber
    # print(str(lightsaber.led_strip))


async def main():
    app = make_app()
    app.listen(6333)

    background_sender = tornado.ioloop.PeriodicCallback(update_sender, WS_SEND_FREQUENCY_SECS * 1000)
    background_sender.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
