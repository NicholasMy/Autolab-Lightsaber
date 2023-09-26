import asyncio
import datetime
import json
from typing import Optional, Awaitable, List, Tuple

import tornado.web
import tornado.websocket
import tornado.ioloop

import config
from AutolabPortalConnection import AutolabPortalConnection
from secret import PORTAL_URL, PORTAL_API_KEY
from timer import Timer
from AnimatedLedStrip import AnimatedLedStrip
from color_map_builder import build_linear_color_map
from infinite_queue import InfiniteQueue


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


portal = AutolabPortalConnection(PORTAL_URL, PORTAL_API_KEY)
lightsaber = AnimatedLedStrip(config.MAX_LED_INDEX, config.DEFAULT_LED_BRIGHTNESS)
old_lightsaber_led_strip = lightsaber.led_strip.copy()
last_update_time = datetime.datetime.now() - datetime.timedelta(seconds=config.DATA_FETCH_SECS)

time_scale_queue: InfiniteQueue = InfiniteQueue(
    [(value, color) for value, color in zip(config.TIME_SCALE_VALUES, config.TIME_SCALE_COLORS)])
time_scale_seconds, time_scale_color = time_scale_queue.next()
time_scale_timer: Timer = Timer(config.TIME_SCALE_CYCLE_SECS)


def update_time_scale():
    global time_scale_seconds, time_scale_color
    time_scale_seconds, time_scale_color = time_scale_queue.next()
    time_scale_timer.reset()
    # print(f"Updated time scale: {time_scale_seconds} seconds")


def get_target_scale_max(value: int) -> Tuple[int, List[int]]:
    if value <= config.VALUE_SCALE_VALUES[0]:
        return config.VALUE_SCALE_VALUES[0], config.VALUE_SCALE_COLORS[0]
    for i, v in enumerate(config.VALUE_SCALE_VALUES):
        if value <= v:
            return config.VALUE_SCALE_VALUES[i], config.VALUE_SCALE_COLORS[i]


def update_target():
    if time_scale_timer.is_done():
        update_time_scale()
    histogram = portal.get_tango_histogram()
    jobs: int = histogram[time_scale_seconds]
    scale_max, scale_color = get_target_scale_max(jobs)
    target_length = int(jobs / scale_max * config.MAX_LED_INDEX)
    color_map = build_linear_color_map(time_scale_color, scale_color, config.MAX_LED_INDEX)
    lightsaber.set_target_state(target_length, color_map, config.ANIMATION_DURATION_SECS)

    # print(f"{time_scale_seconds=}")
    # print(f"{time_scale_color=}")
    # print(f"{target_length=}")
    # print(f"(max) {scale_color=}")
    # print(f"{scale_max=}")
    # print(f"{jobs=}")
    # print("-" * 10)


def update_sender():
    # Computes the current frame of the Lightsaber and broadcasts the difference to all clients
    global lightsaber, old_lightsaber_led_strip, last_update_time

    now = datetime.datetime.now()
    if now - last_update_time > datetime.timedelta(seconds=config.DATA_FETCH_SECS):
        update_target()
        last_update_time = now

    lightsaber.update()
    difference = lightsaber.led_strip.get_difference_map(old_lightsaber_led_strip)
    LightsaberWebSocket.send_updated_state(difference)
    old_lightsaber_led_strip = lightsaber.led_strip.copy()


async def main():
    app = make_app()
    app.listen(6333)

    background_sender = tornado.ioloop.PeriodicCallback(update_sender, config.WS_SEND_FREQUENCY_SECS * 1000)
    background_sender.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
