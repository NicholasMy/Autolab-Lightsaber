from typing import List, Dict

from animated_led_strip import interpolate_rgb


def build_linear_color_map(start: List[int], end: List[int], length: int) -> Dict[int, List[int]]:
    ret: Dict[int, List[int]] = {}
    for i in range(length + 1):
        percent: float = i / length * 100
        ret[i] = interpolate_rgb(start, end, percent)
    return ret
