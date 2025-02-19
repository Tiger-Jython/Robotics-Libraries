from microbit import *
from utime import ticks_us, sleep_us
from neopixel import *

_speedPercent = 50
_powerByteL = 40
_powerByteR = 40
_powerBytesLUT = bytes(b'\x00\x0b\x0b\x0c\x0c\x0d\x0d\x0d\x0e\x0e\x0f\x0f\x0f\x10\x10\x11\x11\x11\x12\x12\x13\x13\x13\x14\x14\x15\x15\x15\x16\x16\x17\x17\x17\x18\x19\x1a\x1b\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x36\x38\x3a\x3c\x3f\x41\x44\x46\x49\x4c\x4f\x53\x56\x5a\x5e\x62\x67\x6b\x70\x75\x7b\x81\x87\x8d\x94\x9b\xa3\xab\xb4\xbd\xc6\xd0\xdb\xe6\xf2\xff')

_powerOffset = 0
_powerDifferential = 0
_arcScaling = 0

_ADDR_ATM = 0x22
_nbLeds = 14


def _setMotors(dirL, powerL, dirR, powerR):
    pinsL = (pin14, pin13)
    pinsR = (pin16, pin15)

    pinsL[dirL].write_analog(powerL)
    pinsL[1 - dirL].write_analog(0)

    pinsR[dirR].write_analog(powerR)
    pinsR[1 - dirR].write_analog(0)


def _setSingleMotor(side, direction, power):
    if side == 0:
        pins = (pin14, pin13)
    elif side == 2:
        pins = (pin16, pin15)

    pins[direction].write_analog(power)
    pins[1 - direction].write_analog(0)


def _getArcBytes(r):
    outerSpeed = _speedPercent
    rCm = int(r * 100)
    threshold = outerSpeed - max(rCm + 20, 40)
    if threshold <= 0:
        outerSpeed = min(max(rCm + 40, 40), 100)
    reducedSpeed = 0
    if rCm >= 4:
        flattening = (100 - outerSpeed) // 2
        reducedSpeed = (rCm * 10 - 35) / \
            (rCm * (11 + (_arcScaling-4)/10) + 90 + flattening)
        reducedSpeed = reducedSpeed * outerSpeed
    innerByte = _getPowerByteLUT(int(reducedSpeed), 0)
    outerByte = _getPowerByteLUT(int(outerSpeed), 0)
    return (innerByte, outerByte)


def calibrate(offset, differential=0, arcScaling=0):
    global _powerDifferential
    global _powerOffset
    global _arcScaling

    _powerOffset = max(min(int(offset), 150), -10)
    _powerDifferential = max(min(int(differential), 150), -150)
    _arcScaling = max(min(arcScaling, 50), -15)
    setSpeed(_speedPercent)


def setSpeed(speed):
    global _speedPercent
    global _powerByteL
    global _powerByteR

    _speedPercent = int(min(max(speed, 0), 100))
    powerByte = _getPowerByteLUT(_speedPercent, _powerOffset)
    boost = round((1 - _speedPercent / 100) *
                  abs(_powerDifferential)) if _speedPercent > 0 else 0
    reduction = round((_speedPercent / 100) * abs(_powerDifferential))
    if _powerDifferential > 0:
        _powerByteL = powerByte - reduction
        _powerByteR = powerByte + boost
    else:
        _powerByteL = powerByte + boost
        _powerByteR = powerByte - reduction


def _getPowerByteLUT(speed, offset):
    speedIndex = int(speed * (len(_powerBytesLUT) - 1) / 100)
    return min(_powerBytesLUT[speedIndex] + offset, 1023)


def stop():
    _setMotors(0, 0, 0, 0)


def forward():
    _setMotors(0, _powerByteL, 0, _powerByteR)


def backward():
    _setMotors(1, _powerByteL, 1, _powerByteR)


def left():
    _setMotors(1, _powerByteL, 0, _powerByteR)


def right():
    _setMotors(0, _powerByteL, 1, _powerByteR)


def rightArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, outer, 0, inner)


def leftArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, inner, 0, outer)


def getDistance():
    pin12.write_digital(1)
    sleep_us(10)
    pin12.write_digital(0)
    pin12.set_pull(pin15.NO_PULL)
    while pin12.read_digital() == 0:
        pass
    start = ticks_us()
    while pin12.read_digital() == 1:
        pass
    end = ticks_us()
    echo = end-start
    distance = int(0.01715 * echo)
    return distance


def setLED(position, red, green, blue):
    global _ADDR_ATM
    i2c_data = bytearray(5)

    i2c_data[0] = 1

    i2c_data[1] = position

    i2c_data[2] = red
    i2c_data[3] = green
    i2c_data[4] = blue

    i2c.write(_ADDR_ATM, i2c_data)


def fill(red, green, blue):
    for position in range(_nbLeds):
        setLED(position, red, green, blue)


def readLine(side):  # 0=left 1=right
    i2c.write(_ADDR_ATM, bytearray([side + 1]), False)
    result = i2c.read(_ADDR_ATM, 2)
    result = result[0] + (result[1] << 8)
    return result


def readLight(side):  # 0=left 1=right
    i2c.write(_ADDR_ATM, bytearray([side + 3]), False)
    result = i2c.read(_ADDR_ATM, 2)
    result = result[0] + (result[1] << 8)
    return result
