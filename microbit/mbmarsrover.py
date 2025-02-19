from microbit import *
from neopixel import *
import utime

_servoArray = [0, 9, 11, 13, 15]
_servoOffset = [0, 0, 0, 0, 0]
_initI2C = False

_nbLeds = 4
_np = NeoPixel(pin2, _nbLeds)

_speedPercent = 50
_powerByteL = 40
_powerByteR = 40

_powerOffset = 0
_powerDifferential = 0
_arcScaling = 0

_MAX_CM_DISTANCE = 500
_CM_PER_MICROSECOND = 29.1


def _setMotors(dirL, powerL, dirR, powerR):
    pinsL = (pin1, pin12)
    pinsR = (pin8, pin0)

    pinsL[dirL].write_analog(powerL)
    pinsL[1 - dirL].write_analog(0)

    pinsR[dirR].write_analog(powerR)
    pinsR[1 - dirR].write_analog(0)


def _setSingleMotor(side, direction, power):
    if side == 0:
        pins = (pin1, pin12)
    elif side == 1:
        pins = (pin8, pin0)

    pins[direction].write_analog(power)
    pins[1 - direction].write_analog(0)


def _getArcBytes(r):
    outerSpeed = _speedPercent
    rCm = int(r * 100)
    threshold = outerSpeed - max(rCm + 20, 40)
    if (threshold <= 0):
        outerSpeed = min(max(rCm + 40, 40), 100)
    reducedSpeed = 0
    if rCm >= 4:
        flattening = (100 - outerSpeed) // 2
        reducedSpeed = (rCm * 10 - 35) / \
            (rCm * (11 + (_arcScaling - 4) / 10) + 90 + flattening)
        reducedSpeed = reducedSpeed * outerSpeed
    innerByte = _convertSpeedToAnalogValue(int(reducedSpeed), 0)
    outerByte = _convertSpeedToAnalogValue(int(outerSpeed), 0)
    return (innerByte, outerByte)


def _initPCA():
    global _initI2C
    _initI2C = True
    i2cData = bytearray(2)
    i2cData[0] = 0
    i2cData[1] = 0x10
    i2c.write(0x40, i2cData)

    i2cData[0] = 0xFE
    i2cData[1] = 101
    i2c.write(0x40, i2cData)

    i2cData[0] = 0
    i2cData[1] = 0x81
    i2c.write(0x40, i2cData)


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


def calibrate(offset, differential=0, arcScaling=0):
    global _powerDifferential
    global _powerOffset
    global _arcScaling

    _powerOffset = max(min(int(offset), 500), -50)
    _powerDifferential = max(min(int(differential), 150), -150)
    _arcScaling = max(min(arcScaling, 50), -15)
    setSpeed(_speedPercent)


def setSpeed(speed):
    global _speedPercent
    global _powerByteL
    global _powerByteR

    _speedPercent = int(min(max(speed, 0), 100))
    powerValue = _convertSpeedToAnalogValue(_speedPercent, _powerOffset)
    boost = round((1 - _speedPercent / 100) *
                  abs(_powerDifferential)) if _speedPercent > 0 else 0
    reduction = round((_speedPercent / 100) * abs(_powerDifferential))
    if _powerDifferential > 0:
        _powerByteL = powerValue - reduction
        _powerByteR = powerValue + boost
    else:
        _powerByteL = powerValue + boost
        _powerByteR = powerValue - reduction


def _convertSpeedToAnalogValue(speed, offset):
    analogValue = int(speed * 1023 / 100) + offset
    return min(max(analogValue, 0), 1023)


def stop():
    _setMotors(0, 0, 0, 0)


def forward():
    _setMotors(0, _powerByteL, 0, _powerByteR)


def backward():
    _setMotors(1, _powerByteL, 1, _powerByteR)


def setServo(servoNum, angle):
    global _servoArray, _initI2C
    if _initI2C == False:
        _initPCA()
    offsetNum = servoNum
    servoNum = _servoArray[servoNum]
    i2cData = bytearray(2)
    start = 0
    angle = max(min(angle, 90), -90)
    stop = 396 + (angle + _servoOffset[offsetNum]) * 223 / 90
    i2cData[0] = 0x06 + servoNum * 4 + 2
    i2cData[1] = int(stop) + 0xff
    i2c.write(0x40, i2cData)

    i2cData[0] = 0x06 + servoNum*4 + 3
    i2cData[1] = int(stop) >> 8
    i2c.write(0x40, i2cData)


def clearServos():
    setServo(0, 0)
    setServo(1, 0)
    setServo(2, 0)
    setServo(3, 0)
    setServo(4, 0)
    sleep(500)


def steer(angle):
    angle = max(min(angle, 45), -45)
    setServo(1, angle)
    setServo(2, -angle)
    setServo(3, -angle)
    setServo(4, angle)
    sleep(500)


def setLED(pos, red, green, blue):
    _np[pos] = (red, green, blue)
    _np.show()


def fill(red, green, blue):
    for i in range(_nbLeds):
        _np[i] = (red, green, blue)
    _np.show()


def getDistance():
    trig = pin13
    echo = pin13

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


def calibrateServo(pos, angleDifferential):
    global _servoOffset

    angleDifferential = max(min(angleDifferential, 90), -90)
    _servoOffset[pos] = angleDifferential
    clearServos()
