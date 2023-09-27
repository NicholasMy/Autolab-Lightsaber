import unittest

from server.animated_led_strip import interpolate, interpolate_rgb


class Test(unittest.TestCase):

    def test_interpolate(self):
        self.assertEqual(interpolate(0, 100, 0), 0)
        self.assertEqual(interpolate(0, 100, 10), 10)
        self.assertEqual(interpolate(0, 200, 50), 100)
        self.assertEqual(interpolate(100, 300, 50), 200)
        self.assertEqual(interpolate(1.0, 3.0, 50), 2.0)
        self.assertEqual(interpolate(1.0, 2.0, 50), 1.5)
        self.assertEqual(interpolate(1.0, 2.0, 25), 1.25)

    def test_interpolate_rgb(self):
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], 0), [0, 0, 0])
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], 10), [10, 10, 10])
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], 50), [50, 50, 50])
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], 100), [100, 100, 100])
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], 200), [100, 100, 100])
        self.assertEqual(interpolate_rgb([0, 0, 0], [100, 100, 100], -100), [0, 0, 0])
        self.assertEqual(interpolate_rgb([50, 100, 200], [50, 200, 100], 50), [50, 150, 150])
        self.assertEqual(interpolate_rgb([50, 100, 200], [50, 200, 100], 75), [50, 175, 125])
        self.assertEqual(interpolate_rgb([100, 100, 100], [99, 100, 101], 0), [100, 100, 100])
        self.assertEqual(interpolate_rgb([100, 100, 100], [99, 100, 101], 49), [100, 100, 100])
        self.assertEqual(interpolate_rgb([100, 100, 100], [99, 100, 101], 51), [99, 100, 101])
        self.assertEqual(interpolate_rgb([100, 100, 100], [99, 100, 101], 100), [99, 100, 101])


if __name__ == '__main__':
    unittest.main()
