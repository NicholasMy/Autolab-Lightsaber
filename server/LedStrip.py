from typing import List


class LedStrip:

    def __init__(self, max_led_index: int, brightness: int):
        self.max_led_index = max_led_index
        self.brightness = brightness
        self.leds = {}
        for i in range(max_led_index + 1):
            self.leds[i] = [0, 0, 0]

    def apply_difference_map(self, difference_map: dict):
        for key in difference_map:
            if key == "brightness":
                self.brightness = difference_map["brightness"]
            else:
                self.leds[key] = difference_map[key]

    def to_dict(self):
        ret = {"brightness": self.brightness}
        for i in range(self.max_led_index + 1):
            ret[i] = self.leds[i]
        return ret

    def copy(self):
        ret = LedStrip(self.max_led_index, self.brightness)
        ret.leds = self.leds.copy()
        return ret

    def clear_leds(self):
        for i in range(self.max_led_index + 1):
            self.leds[i] = [0, 0, 0]

    def get_difference_map(self, previous_led_strip: "LedStrip") -> dict:
        # Return only the keys that have been updated since previous_led_strip
        ret = {}
        old = previous_led_strip.to_dict()
        new = self.to_dict()
        for key in new:
            if key not in old:
                ret[key] = new[key]
            elif new[key] != old[key]:
                ret[key] = new[key]
        return ret

    def fill_range(self, start: int, end: int, color: List[int]):
        start = max(0, start)
        end = min(self.max_led_index, end)
        for i in range(start, end):
            self.leds[i] = color

    def fill_percent(self, percent: float, color: List[int]):
        self.clear_leds()
        self.fill_range(0, int(self.max_led_index * percent / 100), color)

    def __str__(self):
        # Draw the lightsaber as a string of | and spaces, where | is a lit LED and space is an unlit LED
        return "-----" + "".join("|" if self.leds[i] != [0, 0, 0] else " " for i in range(self.max_led_index + 1)) + ")"
