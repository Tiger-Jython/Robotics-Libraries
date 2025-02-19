# mbrobot_plusV2.py
# Date 10/09/24

from microbit import i2c, pin0, pin1, pin2, pin13, pin14, pin15, sleep
import gc
import machine
import music
import neopixel

# Motor state
_speedPercent = 50
_powerByteL = 50
_powerByteR = 50
_motorState = bytearray(5)
_powerBytesLUT = bytes(b'\x00\x0f\x10\x10\x11\x12\x12\x13\x13\x14\x15\x15\x16\x16\x17\x18\x18\x19\x19\x1a\x1b\x1b\x1c\x1c\x1d\x1e\x1e\x1f\x1f\x20\x21\x21\x22\x22\x23\x24\x24\x25\x25\x26\x27\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3b\x3c\x3e\x3f\x41\x43\x45\x47\x49\x4b\x4d\x50\x52\x55\x58\x5b\x5e\x61\x65\x69\x6d\x71\x75\x7a\x7f\x84\x89\x8f\x95\x9b\xa2\xa9\xb1\xb9\xc1\xca\xd3\xdd\xe8\xf3\xff')

# Calibration data
_powerOffset = 0
_powerDifferential = 0
_arcScaling = 0
_servoMinPulse = 25
_servoMaxPulse = 131

# Signaling objects and buffers
_ledState = bytearray(b'\x0B\0\0')
_underglowNP = neopixel.NeoPixel(pin15, 4)
np_rgb_pixels = _underglowNP
_alarmSequence = ['c5:1', 'r', 'c5,1', 'r:3']

_UNCONNECTEDERRORMSG = "Please connect to Maqueen robot and switch it on."

# Utility functions


def _setMotors(dirL, powerL, dirR, powerR):
    # """Write Motor State via i2c

    # Parameters:
    #     dirL (0/1): Direction of left Wheel. 0=forward, 1=backward
    #     powerL (int): Power of left Wheel in range [0,255].
    #     dirR (0/1): Direction of right Wheel. 0=forward, 1=backward
    #     powerR (int): Power of right Wheel in range [0,255].
    #
    # raises:
    #     RuntimeError: if Robot is switched off or unconnected. (replaces ENODEV error)
    # """
    global _motorState
    _motorState[1] = dirL
    _motorState[2] = powerL
    _motorState[3] = dirR
    _motorState[4] = powerR
    try:
        i2c.write(0x10, _motorState)
    except:
        raise RuntimeError(_UNCONNECTEDERRORMSG)


def _setSingleMotor(side, dir, power):
    # """Write Motor State of a single Motor via i2c

    # Parameters:
    #     side (0/2): Selection of the Wheel. 0=left, 2=right
    #     dir (0/1): Direction for that Wheel. 0=forward, 1=backward
    #     power (int): Power for that Wheel in range [0,255].
    #
    # raises:
    #     RuntimeError: if Robot is switched off or unconnected. (replaces ENODEV error)
    # """
    global _motorState
    _motorState[1 + side] = dir
    _motorState[2 + side] = power
    try:
        i2c.write(0x10, _motorState)
    except:
        raise RuntimeError(_UNCONNECTEDERRORMSG)

# _getPowerByte was used to create LookUpTable (_powerBytesLUT) used in _getPowerByteLUT to reduce Memory Leaks.
# def _getPowerByte(speed, offset):
#     # """Computes the power value for a given speed in %.
#     # It accouts for the nonlinearity of motor strength.
#     # This is the original function that generates the LUT.
#
#     # Parameter:
#     #     speed (number): Desired speed of the Robot in %. Range [0,100].
#     #     offset (int): basic power offset to add to the function.
#     # Returns:
#     #     int: Power in range [0,255] to write to the motors via i2c.
#     # """
#     if speed <= 0:
#         return 0
#     elif speed < 40:
#         return int(0.6 * speed + 15 + offset)
#     elif speed < 60:
#         return int(speed + offset)
#     elif speed < 100:
#         return int(min(1.05546 ** speed + 34 + offset, 255))
#     else:
#         return 255


def _getPowerByteLUT(speed, offset):
    # """Lookup Table version of _getPowerByte"""
    return min(_powerBytesLUT[speed] + offset, 255)


def _getArcBytes(r):
    # """Computes the power bytes to drive an arc.

    # Parameter:
    #     r (float): Radius in meters of the desired Arc.
    #         Measured from the center of the axle.
    # Returns:
    #     (int, int): Power byte values for each motor.
    #         First the outer Wheels byte [0,255],
    #         then the inner Wheels byte [0,255].
    # """
    rmm = int(r * 100)  # radius in mm
    outerSpeed = _speedPercent
    # adjust outer speed for unhealthy values
    if outerSpeed < 25:
        outerSpeed = 25
    speedFix = min(abs(outerSpeed - 70), 20) / 20
    reducedSpeed = 0
    if rmm > 5:
        # formula derived from data and simplified
        n = outerSpeed * (3 * _arcScaling - outerSpeed - 9 * rmm + 220)
        d = -14 * _arcScaling + outerSpeed - 200 + 3 * outerSpeed - 10 * rmm - 290
        reducedSpeed = int(n/d)
        if reducedSpeed < 2:  # fix values at low radii (negative values too)
            reducedSpeed = 2 if rmm > 15 else 1
    innerByte = _getPowerByteLUT(int(reducedSpeed), 0)
    outerByte = _getPowerByteLUT(int(outerSpeed), 0)
    return (innerByte, outerByte)

# Movement functions


def calibrate(offset, differential=0, arcScaling=0):
    # """Adjust the driving behaviour of the robots

    # Parameters:
    #     offset (int): Offsets the minimal power of the motors.
    #         Range [-10,50]. Highly affected by battery level.
    #         Adjust this value until it starts moving at speed 1%.
    #     differential (int, optional): Adjusts power difference
    #         of left and right Wheel. Range [-150, 150].
    #         Varies unpredictably with different speeds.
    #         If a Robot steers left when driving forward: negative value
    #         If a Robot steers right when driving forward: positive value
    #         Perfectly straight driving Robots can leave this at 0.
    #     arcScaling (int, optional): Adjusts the radius
    #         driven by leftArc/rightArc. Valid range [-50, 50].
    #         If the Robots radius is too large: positive value
    #         If the Robots radius is too small: negative value
    #         This then adjusts all radii for this Robot, by
    #         scaling it's internal function to the new range.
    # """
    global _powerDifferential
    global _powerOffset
    global _arcScaling
    _powerOffset = max(min(int(offset), 50), -14)
    _powerDifferential = max(min(int(differential), 150), -150)
    _arcScaling = max(min(arcScaling, 50), -50)
    setSpeed(_speedPercent)


def setSpeed(speed):
    # """sets the speed for future motion

    # Parameter:
    #     speed (int): in Range [0,100] as % of desired velocity.
    # """
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


def resetSpeed():
    setSpeed(50)


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
    # """radius must be given in meters."""
    inner, outer = _getArcBytes(radius)
    _setMotors(0, outer, 0, inner)


def leftArc(radius):
    # """radius must be given in meters."""
    inner, outer = _getArcBytes(radius)
    _setMotors(0, inner, 0, outer)


class Motor:
    def __init__(self, side):
        # """Create a single motor.

        # Parameter:
        #     side (0/2): 0=left, 2=right
        # """
        self._side = side

    def rotate(self, speed):
        # """Controls rotation of this motor.

        # Parameters:
        #     speed (int): Desired speed in %.
        #         Valid range [-100,100].
        #         Negative values are for backward turning.
        # """
        speedClamped = int(min(max(abs(speed), 0), 100))
        power = _getPowerByteLUT(speedClamped, _powerOffset)
        direction = 0 if speed > 0 else 1
        _setSingleMotor(self._side, direction, power)


def setServo(servo, angle):
    # """Moves the Servo to position angle.
    # Servos must be connected to the Maqueen Plus V2's "P" connectors.
    # They are located at the back of the robot.

    # Parameters:
    #     servo (str): Desired Servo Port. Either 'P0', 'P1' or 'P2'.
    #     angle (int): Desired angle in degrees. Range [0,180].

    # raises:
    #     ValueError: if arguments are out of valid range
    # """
    if servo == "P0" or servo == 'S1':
        pin = pin0
    elif servo == "P1" or servo == 'S2':
        pin = pin1
    elif servo == "P2":
        pin = pin2
    else:
        raise ValueError("Unknown Servo. Please use 'P0', 'P1' or 'P2'.")

    if angle < 0 or angle > 180:
        raise ValueError("Invalid angle. Must be between 0 and 180")

    frac = (_servoMaxPulse - _servoMinPulse) * int(angle)
    offset = (frac >> 8) + (frac >> 10) + (frac >> 11) + (frac >> 12)  # / 180
    usPulseTime = _servoMinPulse + offset  # min + (max-min) * (angle / 180)
    pin.set_analog_period(20)
    pin.write_analog(usPulseTime)


def setMinAngleVal(duty):
    # """ Sets the minimal pulse duty cycle for the servo.
    # It should match 1ms of a 20ms period, where the duty is in range [0,1024].
    # Theoretically: 1/20*1024 = 51. Practically: Default is 25. adjust carefully in steps of 1.
    #
    # Parameter:
    #     duty (int): The minimal duty amount for a write_analog signal with 20ms pulse.
    #         It should approximate 1ms. 1ms/20ms*1024 = min duty = 0-degree position for the servo.
    # """
    global _servoMinPulse
    _servoMinPulse = int(duty)


def setMaxAngleVal(duty):
    # """ Sets the maximal pulse duty cycle for the servo.
    # It should match 2ms of a 20ms period, where the duty is in range [0,1024].
    # Theoretically: 2/20*1024 = 102. Practically: Default is 131. adjust carefully to increase range of the servo.
    #
    # Parameter:
    #     duty (int): The maximal duty amount for a write_analog signal with 20ms pulse.
    #         It should approximate 2ms. 2ms/20ms*1024 = max duty = 180-degree position for the servo.
    # """
    global _servoMaxPulse
    _servoMaxPulse = int(duty)

# Sensor functions


class IRSensor:
    _address = bytes(b'\x1D')

    def __init__(self, index):
        # """Create a new IR sensor.

        # Parameter:
        #     index (int): 0=R2, 1=R1, 2=M, 3=L1, 4=L2
        # """
        self._index = index

    def read_digital(self):
        # """Returns if the surface below is dark or bright.
        # Result can be adjusted by putting the sensor on the dark
        # surface and pressing the LineKey calibration button on the
        # Robot for a few seconds, until the LED's blink.

        # Returns:
        #     0 if the surface is dark. No light was reflected (in Air).
        #     1 if the surface is bright. A lot of light was reflected.
        #
        # raises:
        #     RuntimeError: if Robot is switched off or unconnected. (replaces ENODEV error)
        # """
        try:
            i2c.write(0x10, IRSensor._address)
        except:
            raise RuntimeError(_UNCONNECTEDERRORMSG)
        byte = ~i2c.read(0x10, 1)[0]
        # mask out corresponding bit, from returned byte.
        return (byte & (2 ** self._index)) >> self._index

    def read_analog(self):
        # """Returns the brightness of the surface as a byte.

        # Returns:
        #     int: amount of reflection of light in range [0,255].
        #
        # raises:
        #     RuntimeError: if Robot is switched off or unconnected. (replaces ENODEV error)
        # """
        try:
            i2c.write(0x10, IRSensor._address)
        except:
            raise RuntimeError(_UNCONNECTEDERRORMSG)
        # Buffer structure:
        # 1 Byte Bitmask (for digital redout),
        # then 10 Bytes analog byte values (every second entry is a value).
        buffer = i2c.read(0x10, 11)
        return buffer[1 + self._index * 2]


def ir_read_values_as_byte():
    # """get single byte with bit encoding of each Infrared sensor state
    #  Bits: 0=R2, 1=R1, 2=M, 3=L1, 4=L2
    # """
    i2c.write(0x10, bytearray([0x1D]))
    buf = i2c.read(0x10, 1)
    return ~buf[0]


def getDistance():
    # """uses the ultrasonic sensor to measure distance

    # Returns:
    #     int: valid Distance as cm in range [0,500].
    #         For measurement errors or larger distances: 255.
    # """
    pin13.write_digital(1)
    pin13.write_digital(0)
    p = machine.time_pulse_us(pin14, 1, 50000)
    # approximate division: p / 58.2 - 0.5
    cm = (p >> 6) + (p >> 10) + (p >> 11) + (p >> 12) + 1
    return max(min(cm, 500), 0) if cm > 0 else 255

# Signaling functions


def setLED(state, stateR=None):
    # """Set the front red LED's.

    # Parameters:
    #     state (0/1): Sets the state of the left LED.
    #         if stateR is omitted, then both LEDS.
    #         0=Off, 1=On
    #     stateR (0/1/None, optional): Sets the right LED state.
    #         0=Off, 1=On, Default=None uses "state" for right LED.
    # """
    global _ledState
    stateR = stateR if stateR != None else state
    _ledState[1] = state
    _ledState[2] = stateR
    i2c.write(0x10, _ledState)


def setLEDLeft(state):
    # """state: 0=Off, 1=On"""
    global _ledState
    _ledState[1] = state
    i2c.write(0x10, _ledState)


def setLEDRight(state):
    # """state: 0=Off, 1=On"""
    global _ledState
    _ledState[2] = state
    i2c.write(0x10, _ledState)


def fillRGB(red, green, blue):
    # """Uses Neopixel to set all 4 bottom RGB LEDs color.
    # Parameters (red,green,blue) are each a byte in Range [0,255].
    # """
    for i in range(4):
        _underglowNP[i] = (red, green, blue)
    _underglowNP.show()


def clearRGB():
    _underglowNP.clear()


def setRGB(position, red, green, blue):
    # """Uses Neopixel to set a single RGB LED of the robot.

    # Parameters:
    #     position (int): position of the targeted LED.
    #         Numbers are visible at underside of Robot.
    #         0=front left
    #         1=back left
    #         2=back right
    #         3=front right
    #     red, green, blue (int): color byte value.
    #         each in range [0,255].

    # raises:
    #     ValueError: if position argument is out of valid range
    # """
    if position < 0 or position > 3:
        raise ValueError("invalid RGB-LED position. Must be 0,1,2 or 3.")
    _underglowNP[position] = (red, green, blue)
    _underglowNP.show()


def setAlarm(state):
    if state:
        music.play(_alarmSequence, wait=False, loop=True)
    else:
        music.stop()


def beep():
    music.pitch(440, 200, wait=False)

# Class constants (for compatibilty)


class LEDState:
    ON = 1
    OFF = 0
    RED = 1


class IR:
    R2 = 0
    R1 = 1
    M = 2
    L1 = 3
    L2 = 4
    masks = [0x01, 0x02, 0x04, 0x08, 0x10]


# Default instances
pin2.set_pull(pin2.NO_PULL)
delay = sleep
irR2 = IRSensor(0)
irR1 = IRSensor(1)
irRight = irR1
irM = IRSensor(2)
irL1 = IRSensor(3)
irLeft = irL1
irL2 = IRSensor(4)
motL = Motor(0)
motR = Motor(2)
