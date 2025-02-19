from microbit import *
from neopixel import *
import utime

_nbLeds = 4
_np = NeoPixel(pin13, _nbLeds)

_speedPercent = 50
_powerLeft = 90
_powerRight = 90

_powerOffset = 0
_powerDifferential = 0
_arcScaling = 0

_MAX_CM_DISTANCE = 500
_CM_PER_MICROSECOND = 29.1


def _setMotors(dirL, powerL, dirR, powerR):
    pin8.write_analog(powerL if dirL == 1 else 0)
    pin12.write_analog(0 if dirL == 1 else powerL)
    pin16.write_analog(0 if dirR == 1 else powerR)
    pin14.write_analog(powerR if dirR == 1 else 0)


def _pulse_in(pin, value, timeout):
    start_time = utime.ticks_us()
    while pin.read_digital() != value:
        if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
            return 0
    start_time = utime.ticks_us()
    while pin.read_digital() == value:
        if utime.ticks_diff(utime.ticks_us(), start_time) > timeout:
            return 0
    return utime.ticks_diff(utime.ticks_us(), start_time)


def _getArcBytes(r):
    outerSpeed = _speedPercent
    if r > 0:
        innerSpeed = outerSpeed * max(0.2, min(1, 1 - r / 100))
    else:
        innerSpeed = 0

    innerByte = _convertSpeedToAnalogValue(int(innerSpeed), 0)
    outerByte = _convertSpeedToAnalogValue(int(outerSpeed), 0)
    return (innerByte, outerByte)


def _convertSpeedToAnalogValue(speed, offset):
    analogValue = int(speed * 255 / 100) + offset
    return min(max(analogValue, 0), 255)


def calibrate(offset, differential=0, arcScaling=0):
    global _powerDifferential
    global _powerOffset
    global _arcScaling
    _powerOffset = max(min(int(offset), 100), -10)
    _powerDifferential = max(min(int(differential), 150), -150)
    _arcScaling = max(min(arcScaling, 50), -15)
    setSpeed(_speedPercent)


def setSpeed(speed):
    global _speedPercent
    global _powerLeft
    global _powerRight
    _speedPercent = int(min(max(speed, 0), 100))
    powerByte = _convertSpeedToAnalogValue(_speedPercent, _powerOffset)
    boost = round((1 - _speedPercent / 100) *
                  abs(_powerDifferential)) if _speedPercent > 0 else 0
    reduction = round((_speedPercent / 100) * abs(_powerDifferential))
    if _powerDifferential > 0:
        _powerLeft = powerByte - reduction
        _powerRight = powerByte + boost
    else:
        _powerLeft = powerByte + boost
        _powerRight = powerByte - reduction


def stop():
    _setMotors(0, 0, 0, 0)


def forward():
    _setMotors(0, _powerLeft, 0, _powerRight)


def backward():
    _setMotors(1, _powerLeft, 1, _powerRight)


def left():
    _setMotors(1, _powerLeft, 0, _powerRight)


def right():
    _setMotors(0, _powerLeft, 1, _powerRight)


def rightArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, outer, 0, inner)


def leftArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, inner, 0, outer)


def setLED(pos, red, green, blue):
    _np[pos] = (red, green, blue)
    _np.show()


def fill(red, green, blue):
    for i in range(_nbLeds):
        _np[i] = (red, green, blue)
    _np.show()


def getDistance():
    trig = pin15
    echo = pin15
    d = 10
    trig.set_pull(trig.NO_PULL)
    for _ in range(10):
        trig.write_digital(0)
        utime.sleep_us(2)
        trig.write_digital(1)
        utime.sleep_us(10)
        trig.write_digital(0)
        duration = _pulse_in(echo, 1, _MAX_CM_DISTANCE * _CM_PER_MICROSECOND)
        if duration > 0:
            d = duration
            break
    return round(d / _CM_PER_MICROSECOND)
