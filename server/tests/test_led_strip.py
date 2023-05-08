import unittest

from server.LedStrip import LedStrip


class Test(unittest.TestCase):

    def test_fill_range(self):
        strip = LedStrip(165, 5)

        # Test the beginning of the strip
        strip.fill_range(0, 5, [255, 0, 0])
        for i in range(6):
            self.assertEqual(strip.leds[i], [255, 0, 0], f"Failed at {i=}")

        # Test the end of the strip
        strip.fill_range(160, 165, [0, 255, 0])
        for i in range(160, 166):
            self.assertEqual(strip.leds[i], [0, 255, 0], f"Failed at {i=}")

        # Ensure that the middle of the strip is still black
        for i in range(6, 160):
            self.assertEqual(strip.leds[i], [0, 0, 0], f"Failed at {i=}")

    def test_fill_percent(self):
        strip = LedStrip(165, 5)
        strip.fill_percent(100, [255, 0, 0])
        for i in range(166):
            self.assertEqual(strip.leds[i], [255, 0, 0], f"Failed at {i=}")


if __name__ == '__main__':
    unittest.main()
