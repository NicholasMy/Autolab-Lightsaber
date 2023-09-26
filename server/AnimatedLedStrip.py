import datetime
from typing import Dict, List

import config
from LedStrip import LedStrip


def interpolate(start: float, end: float, percent: float) -> float:
    # Return the value that is percent of the way between start and end
    if percent > 100.0:
        percent = 100.0
    elif percent < 0.0:
        percent = 0.0
    return start + (end - start) * percent / 100.0


def interpolate_rgb(start: List[int], end: List[int], percent: float) -> List[int]:
    return [int(interpolate(start[0], end[0], percent) + 0.5),
            int(interpolate(start[1], end[1], percent) + 0.5),
            int(interpolate(start[2], end[2], percent) + 0.5)]


class AnimatedLedStrip:
    # Allows animating the length of the lit portion of the lightsaber and fading between colors on LEDs that stay lit
    def __init__(self, max_led_index: int, brightness: int):
        self.led_strip = LedStrip(max_led_index, brightness)
        self.animating = False  # Whether an animation is currently running
        # "previous" refers to the state of the lightsaber before the current animation started
        # "target" refers to the state of the lightsaber at the end of the current animation
        # "last" refers to the state of the lightsaber at the end of the most recent update (mid-animation)
        # "current" refers to the current animation as a whole
        self.previous_length = 0
        self.last_length = 0
        self.target_length = 0

        self.default_color = [255, 0, 0]
        self.previous_color_map: Dict[int, List[int]] = {}
        self.target_color_map: Dict[int, List[int]] = {}  # Maps LED index to color to allow gradients

        self.current_animation_start_time = datetime.datetime.now()
        self.current_animation_end_time = datetime.datetime.now()

    def update(self):
        # Update self.led_strip to current state according to time remaining in current animation

        if not self.animating:
            return

        now = datetime.datetime.now()

        animation_percent_elapsed = (now - self.current_animation_start_time) / (
                self.current_animation_end_time - self.current_animation_start_time) * 100.0

        if now > self.current_animation_end_time:
            animation_percent_elapsed = 100.0
            # The animation may not be complete yet, so we need to do one last cycle
        if now < self.current_animation_start_time:
            self.animating = False
            return

        current_length = int(
            self.previous_length + (self.target_length - self.previous_length) * animation_percent_elapsed / 100.0)

        if current_length < self.previous_length:
            # Lightsaber is retracting
            for i in range(int(current_length) + 1, self.last_length + 1):
                # Turn off the LEDs that are no longer lit at this time
                self.led_strip.leds[i] = [0, 0, 0]

        for i in range(current_length + 1):
            # Fade the old and new LEDs to the target color, new LEDs turn on as the animation percent increases
            target_color = self.target_color_map.get(i, self.default_color)
            previous_color = self.previous_color_map.get(i, self.default_color)
            new_color = interpolate_rgb(previous_color, target_color, animation_percent_elapsed)
            self.led_strip.leds[i] = new_color

        self.last_length = current_length

        if config.ALWAYS_SHOW_MAX_SCALE_COLOR:
            for i in range(self.led_strip.max_led_index - 2, self.led_strip.max_led_index + 1):
                target_color = self.target_color_map.get(i, self.default_color)
                previous_color = self.previous_color_map.get(i, self.default_color)
                new_color = interpolate_rgb(previous_color, target_color, animation_percent_elapsed)
                self.led_strip.leds[i] = new_color

        if animation_percent_elapsed == 100.0:
            # Animation is over
            self.previous_length = self.target_length
            self.previous_color_map = self.target_color_map
            self.animating = False

    def set_target_state(self, length: int, color_map: Dict[int, List[int]], duration: float):
        # Set the target state of the lightsaber and start the animation
        self.previous_length = self.last_length
        self.target_length = length
        self.previous_color_map = self.led_strip.leds
        self.target_color_map = color_map

        now = datetime.datetime.now()
        self.current_animation_start_time = now
        self.current_animation_end_time = now + datetime.timedelta(seconds=duration)
        self.animating = True
        print("Animating to length " + str(length) + " over " + str(duration) + " seconds")
