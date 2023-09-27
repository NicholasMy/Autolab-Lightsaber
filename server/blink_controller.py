from led_strip import LedStrip
from timer import Timer


class BlinkController:

    def __init__(self, blink_led_strip: LedStrip, blink_off_time: float, blink_on_time: float):
        # blink_led_strip is the LED strip state that will show when blinking
        # blink_off_time is the time in seconds between blinks, where the original LED strip will be shown
        # blink_on_time is the time in seconds that the LED strip will be off (showing the blink_led_strip)
        self.blink_led_strip = blink_led_strip
        self.blink_off_time = blink_off_time
        self.blink_on_time = blink_on_time
        self.blink_timer = Timer(0.0)
        self.blink_on = False
        self.remaining_blinks = 0

    def set_blinks(self, blink_count: int):
        self.remaining_blinks = blink_count
        if blink_count > 0:
            self.blink_timer.reset()
            self.blink_on = True
        if blink_count == 0:
            self.blink_on = False

    def get_led_strip(self, original_led_strip: LedStrip):
        # If currently blinking, return blink_led_strip, otherwise return original_led_strip

        if self.remaining_blinks > 0:
            # print(f"{self.remaining_blinks=} {self.blink_on=}")
            if self.blink_timer.is_done():
                if self.blink_on:
                    self.blink_timer.set_duration(self.blink_off_time)
                    self.blink_on = False
                    self.remaining_blinks -= 1
                    print(f"Finished blink. Now: {self.remaining_blinks=} {self.blink_on=}")
                else:
                    self.blink_timer.set_duration(self.blink_on_time)
                    self.blink_on = True
                    print(f"Starting blink. Now: {self.remaining_blinks=} {self.blink_on=}")
                self.blink_timer.reset()

        if self.blink_on:
            return self.blink_led_strip
        else:
            return original_led_strip
