from microbit import *
from neopixel import *
from utime import ticks_us, sleep_us


_v = 200
_nbLeds = 12
_np = NeoPixel(pin13, _nbLeds)

_powerDifferential = 0
_powerOffset = 0


def w(leftforward, leftbackward, rightforward, rightbackward):
    if leftforward > 0 or rightforward > 0:
        pin16.write_analog(leftforward + _powerDifferential)
        pin8.write_analog(leftbackward)
        pin14.write_analog(rightforward - _powerDifferential)
        pin12.write_analog(rightbackward)
    elif leftbackward > 0 or rightbackward > 0:
        pin16.write_analog(leftforward)
        pin8.write_analog(leftbackward + _powerDifferential)
        pin14.write_analog(rightforward)
        pin12.write_analog(rightbackward - _powerDifferential)
    elif leftforward == 0 and rightforward == 0 and leftbackward == 0 and rightbackward == 0:
        pin16.write_analog(0)
        pin8.write_analog(0)
        pin14.write_analog(0)
        pin12.write_analog(0)


def forward():
    w(_v, 0, _v, 0)


def backward():
    w(0, _v, 0, _v)


def stop():
    w(0, 0, 0, 0)


def right():
    w(0, _v, _v, 0)


def left():
    w(_v, 0, 0, _v)


def set_led(pos, red, green, blue):
    _np[pos] = (red, green, blue)
    _np.show()


def fill(red, green, blue):
    for i in range(_nbLeds):
        _np[i] = (red, green, blue)
    _np.show()


def getDistance():
    pin15.write_digital(1)
    sleep_us(10)
    pin15.write_digital(0)
    pin15.set_pull(pin15.NO_PULL)
    while pin15.read_digital() == 0:
        pass
    start = ticks_us()
    while pin15.read_digital() == 1:
        pass
    end = ticks_us()
    echo = end-start
    distance = int(0.01715 * echo)
    return distance


def calibrate(offset, differential=0):
    global _powerDifferential
    global _powerOffset
    global _arcScaling

    _powerOffset = max(min(int(offset), 50), -50)
    _powerDifferential = max(min(int(differential), 50), -50)
    _arcScaling = max(min(arcScaling, 50), -50)
    setSpeed(_v / 1023 * 100)


def setSpeed(percent):
    global _v
    speed = percent / 100 * 1023
    speed += _powerOffset/100 * 1023
    speed = min(max(speed, 0), 1023)
    _v = speed


def getLine(bit):
    mask = 1 << bit
    value = 0
    try:
        value = i2c.read(0x1c, 1)[0]
    except OSError:
        pass
    if (value & mask) > 0:
        return 1
    else:
        return 0


def getLight(index):
    if index == 0:
        return pin1.read_analog()
    elif index == 1:
        return pin2.read_analog()


def leftArc(radius):
    speed = _v
    inner_wheel_speed = speed * (radius / (radius + 1))
    w(inner_wheel_speed, 0, speed, 0)


def rightArc(radius):
    speed = _v
    inner_wheel_speed = speed * (radius / (radius + 1))
    w(speed, 0, inner_wheel_speed, 0)
