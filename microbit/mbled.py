from neopixel import *
import gc
from microbit import pin2


_nbLeds = 24
_np = NeoPixel(pin2, _nbLeds)

# Fill all pixels with the same color.
# The color is specified by giving values between 0 and 255 for red, green and blue


def fill(red, green, blue):
    for i in range(_nbLeds):
        _np[i] = (red, green, blue)
    _np.show()

# Set the specified pixel to the specified color.
# The pixel is specified by a number between 0 and 23.
# The color is specified by giving values between 0 and 255 for red, green and blue


def set_led(pos, red, green, blue):
    _np[pos] = (red, green, blue)
    _np.show()

# clears all LEDS by turning them off


def clear():
    _np.clear()

# shift the displayed image by as many led-positions as specified in parameter "amount".
# LED strip behaves like a cycle and wraps around when shifting across borders.


def shift_by(amount):
    shifted_copy = [None]*_nbLeds
    for n in range(0, _nbLeds):
        next_i = (n + amount) % _nbLeds
        shifted_copy[n] = _np[next_i]
    for n in range(0, _nbLeds):
        _np[n] = shifted_copy[n]
    _np.show()

# get linearly interpolated colors in RGB space.
# "percent" is the blending distance between the two colors. 0 is first color only, and 100 is second color only.


def lerp_RGB(r1, g1, b1, r2, g2, b2, percent):
    if percent < 0.0 or percent > 100.0:
        raise RuntimeError("Argument 'percent' must be between 0 and 100.")
    red = max(0, min(255, round(r1 + (r2 - r1) * (percent/100.0))))
    green = max(0, min(255, round(g1 + (g2 - g1) * (percent/100.0))))
    blue = max(0, min(255, round(b1 + (b2 - b1) * (percent/100.0))))
    return red, green, blue
