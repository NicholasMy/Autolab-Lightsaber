import asyncio
import datetime
import json
from typing import Optional, Awaitable, List, Tuple

import tornado.web
import tornado.websocket
import tornado.ioloop

import config
from autolab_portal_connection import AutolabPortalConnection
from secret import PORTAL_URL, PORTAL_API_KEY
from blink_controller import BlinkController
from led_strip import LedStrip
from timer import Timer
from animated_led_strip import AnimatedLedStrip
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
    def send_updated_state_json(json_str: str):
        # Separated from send_updated_state so that the JSON can be precomputed elsewhere
        # to improve performance when sending updates rapidly.
        # Most of the time, send_updated_state is performant enough.
        LightsaberWebSocket.broadcast(json_str)

    @staticmethod
    def send_updated_state(update_map: dict):
        # Called when the light needs to update
        LightsaberWebSocket.send_updated_state_json(json.dumps(update_map))


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
blink_led_strip: LedStrip = LedStrip(config.MAX_LED_INDEX, config.DEFAULT_LED_BRIGHTNESS)  # Default empty LED strip
blink_controller: BlinkController = BlinkController(blink_led_strip, config.BLINK_TIME_SECS, config.BLINK_TIME_SECS)


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
    if config.BLINK_ON_SUBMISSION:
        new_submissions: int = histogram[int(config.DATA_FETCH_SECS)]
        blink_controller.set_blinks(new_submissions)


def update_sender():
    # Computes the current frame of the Lightsaber and broadcasts the difference to all clients
    global lightsaber, old_lightsaber_led_strip, last_update_time

    now = datetime.datetime.now()
    if now - last_update_time > datetime.timedelta(seconds=config.DATA_FETCH_SECS):
        update_target()
        last_update_time = now

    lightsaber.update()
    blinking_led_strip: LedStrip = blink_controller.get_led_strip(lightsaber.led_strip)
    difference = blinking_led_strip.get_difference_map(old_lightsaber_led_strip)

    if len(difference) < 20:
        LightsaberWebSocket.send_updated_state(difference)
    else:
        # If difference is too large, split it into multiple messages.
        # The microcontroller can't load the whole difference into memory at once.
        # Splitting it up into more parts than necessary makes the animation look smoother.
        # Too many parts will cancel out the smooth growing/shrinking effect after a blink.
        n = 2
        pieces: List[dict] = [{} for _ in range(n)]

        diff_len = len(difference)
        for i, (k, v) in enumerate(difference.items()):
            index = int(i / diff_len * n)
            pieces[index][k] = v

        # Precomputing the JSON here reduces the time between sending pieces
        json_pieces: List[str] = [json.dumps(piece) for piece in pieces]
        for piece in json_pieces:
            LightsaberWebSocket.send_updated_state_json(piece)

    old_lightsaber_led_strip = blinking_led_strip.copy()


async def main():
    app = make_app()
    app.listen(6333)

    background_sender = tornado.ioloop.PeriodicCallback(update_sender, config.WS_SEND_FREQUENCY_SECS * 1000)
    background_sender.start()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
