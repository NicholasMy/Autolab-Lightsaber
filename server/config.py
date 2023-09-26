MAX_LED_INDEX: int = 165
DEFAULT_LED_BRIGHTNESS: int = 100
ANIMATION_DURATION_SECS: float = 2.0
DATA_FETCH_SECS: float = 3.0
WS_SEND_FREQUENCY_SECS: float = 0.1  # This should actually be much smaller (faster)

TIME_SCALE_VALUES = [30, 60, 600, 3600, 7200, 86400]  # In seconds
TIME_SCALE_COLORS = [
    [0, 0, 255],
    [255, 0, 255],
    [0, 255, 0],
    [255, 255, 0],
    [255, 128, 0],
    [255, 0, 0],
]

VALUE_SCALE_VALUES = [4, 8, 32, 64, 256, 1024]  # Upper bound for number of submissions in time period
VALUE_SCALE_COLORS = [
    [0, 0, 255],
    [255, 0, 255],
    [0, 255, 0],
    [255, 255, 0],
    [255, 128, 0],
    [255, 0, 0],
]

# This requires precise time synchronization between DATA_FETCH_SECS above and
# TANGO_MAX_POLL_RATE in the Autolab Portal config.
# Additionally, `int(DATA_FETCH_SECS)` must exist in the histogram dict.
BLINK_ON_SUBMISSION: bool = True

# Should 3 LEDs always be lit up at the max scale? This helps to understand the scale when the bar isn't very long.
ALWAYS_SHOW_MAX_SCALE_COLOR: bool = True
