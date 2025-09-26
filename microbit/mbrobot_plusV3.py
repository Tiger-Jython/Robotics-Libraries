# mbrobot_plusV2.py
# Date 26/09/25

from microbit import i2c, sleep, running_time, pin2, pin1
import neopixel
import music


# Motor state
_motorState = bytearray(5)
_powerByteL = 50
_powerByteR = 50
_arcScaling = 0

_UNCONNECTEDERRORMSG = "Please connect to Maqueen robot and switch it on."

# Signaling objects and buffers

_ledState = bytearray(b'\x0B\0\0')
_underglowNP = neopixel.NeoPixel(pin1, 4)
_alarmSequence = ['c5:1', 'r', 'c5,1', 'r:3']

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


def setSpeed(speed):
    global _speedPercent
    global _powerByteL
    global _powerByteR
    _speedPercent = int(min(max(speed,0),100))
    _powerByteL = speed
    _powerByteR = speed


def resetSpeed():
    setSpeed(50)


def stop():
    _setMotors(0,0,0,0)


def forward():
    _setMotors(0, _powerByteL, 0, _powerByteR)


def backward():
    _setMotors(1, _powerByteL, 1, _powerByteR)


def left():
    _setMotors(1, _powerByteL, 0, _powerByteR)
    

def right():
    _setMotors(0, _powerByteL, 1, _powerByteR)


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
    innerByte = int(reducedSpeed)
    outerByte = int(outerSpeed)
    return (innerByte, outerByte)


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
        power = speedClamped
        direction = 0 if speed > 0 else 1
        _setSingleMotor(self._side, direction, power)


class IRSensor:
    _address = bytes(b'\x1D') 

    def __init__(self, index):
        self.index = index


    def read_digital(self):
        try:
            i2c.write(0x10, IRSensor._address)
        except:
            raise RuntimeError(_UNCONNECTEDERRORMSG)
        byte = ~i2c.read(0x10, 1)[0]
        # mask out corresponding bit, from returned byte.
        return (byte & (2 ** self._index)) >> self._index


    def read_analog(self):
        buff = bytearray(1)
        try:
            buff[0] = 0x1D
            i2c.write(0x10, buff)
        except:
            raise RuntimeError(_UNCONNECTEDERRORMSG)
        # Buffer structure: 
        # 1 Byte Bitmask (for digital redout), 
        # then 10 Bytes analog byte values (every second entry is a value).
        buffer = i2c.read(0x10,11)
        return buffer[2+2*self.index] << 8 | buffer[1+2*self.index]


def setLEDs(rgbl, rgbr):
    # Front RGB LED
    # dir_type: 11=left, 12=right
    # rgb: 0 - 8
    LEDState = bytearray(2)
    LEDState[1] = rgbl
    LEDState[0] = 11
    i2c.write(0x10, LEDState)
    LEDState[1] = rgbr
    LEDState[0] = 12
    i2c.write(0x10, LEDState)


def fillRGB(red, green, blue):
    _underglowNP.fill((red,green,blue))
    _underglowNP.show()


def clearRGB():
    _underglowNP.clear()


def setRGB(position, red, green, blue):
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
stop()


# Light Intensity ##########################################################################

#side: 1=left, 2=right
def readLightIntensity(side):
    buff = bytearray(1)
    buff[0] = 78
    i2c.write(0x10, buff)
    LightBuffer = i2c.read(0x10, 4, repeat=False)
    if side == 1:

        return LightBuffer[0] << 8 | LightBuffer[1]
    else:
        return LightBuffer[2] << 8 | LightBuffer[3]


# Automatic Line Detection #################################################################

# speed: 0 to 4
def setPatrolSpeed(speed):
    buff = bytearray(2)
    buff[0] = 63
    buff[1] = speed
    i2c.write(0x10, buff)


# 1=left, 2=right, 3=straigt, 4=stop
def setIntersectionRunMode(mode):
    buff = bytearray(2)
    buff[0] = 69
    buff[1] = mode
    i2c.write(0x10, buff)


# T-Junction mode

# 1=left, 2=right, 4=stop
def setTRordRunMode(mode):
    buff = bytearray(2)
    buff[0] = 70
    buff[1] = mode
    i2c.write(0x10, buff)


# 3=straight, 1=left, 4=stop
def setLeftOrStraightRunMode(mode):
    buff = bytearray(2)
    buff[0] = 71
    buff[1] = mode
    i2c.write(0x10, buff)


# 3=straight, 2=right, 4=stop
def setRightOrStraightRunMode(mode):
    buff = bytearray(2)
    buff[0] = 72
    buff[1] = mode
    i2c.write(0x10, buff)


# on=1, off=2
def patrolling(patrol):
    buff = bytearray(2)
    buff[0] = 60
    if patrol == 1:
        buff[1] = 0x04 | 0x01
    else:
        buff[1] = 0x08
    i2c.write(0x10, buff)


def intersectionDetecting():
    buf = bytearray(1)
    buf[0] = 61
    i2c.write(0x10, buf)
    data = i2c.read(0x10, 1)[0]
    return data


# PID Motor Control #####################################################################

def pidControlDistance(dir, distance, interruption):
    # dir: cw=1, ccw=2
    # dist: cm
    # interrupt: 0=allowed, 1=not_allowed
    speed = 2
    buff = bytearray(2)
    if distance >= 6000:
        distance = 60000
    buff[0] = 64 
    buff[1] = dir
    i2c.write(0x10, buff)
    buff[0] = 85
    buff[1] = speed
    i2c.write(0x10, buff)
    buff[0] = 65
    buff[1] = distance >> 8
    i2c.write(0x10, buff)
    buff[0] = 66
    buff[1] = distance
    i2c.write(0x10, buff)
    buff[0] = 60
    buff[1] = 0x04 | 0x02
    i2c.write(0x10, buff)
    if (interruption == 1):
        i2c.write(0x10, 87)
        buff = bytearray(1)
        buff = i2c.read(0x10, 1)
        while flagBuffer[0] == 1:
            sleep(10)
            flagBuffer = i2c.read(0x10, 1)


def pidControlAngle(angle, interruption):
    # angle: -180 to 180, default 90
    # interruption: 0=allowed, 1=not_allowed
    speed = 2
    buff = bytearray(2)
    buff[0] = 67
    if angle >= 0:
        buff[1] = 1
    else:
        buff[1] = 2
        angle = -angle
    i2c.write(0x10, buff)
    buff[0] = 86
    buff[1] = speed
    i2c.write(0x10, buff)
    buff[0] = 68
    buff[1] = angle
    i2c.write(0x10, buff)
    buff[0] = 60
    buff[1] = 0x04 | 0x02
    i2c.write(0x10, buff)
    if interruption == 1:
        i2c.write(0x10, 87)
        buff = bytearray(1)
        buff = i2c.read(0x10, 1)
        while buff[0] == 1:
            sleep(10)
            buff = i2c.read(0x10, 1)


def pidControlStop():
    buff = bytearray(2)
    buff[0] = 60
    buff[1] = 0x10
    i2c.write(0x10, buff)


#type: 1=left, 2=right
def readRealTimeSpeed(type):
    buff = bytearray(2)
    buff[0] = 76
    buff[1] = 1
    i2c.write(0x10, buff)
    buff = i2c.read(0x10, 2)
    if type == 1:
        return buff[0] / 5
    else:
        return buff[1] / 5


# LIDAR Code #########################################################################

def _sendLidarCommand(cmd, args=[]):
    # cmd: command byte
    # args: optional arguments for command
    args_len = len(args)
    packet_len = args_len + 1 # args + commmand
    packet = bytearray(4 + args_len) # header + args
    # 1 byte address, 2 bytes length, 1 byte command
    packet[0] = 0x55
    packet[1] = (packet_len >> 8) & 0xFF
    packet[2] = packet_len & 0xFF
    packet[3] = cmd
    for i, arg in enumerate(args):
        packet[4 + i] = arg
    # chunkwise sending? TODO
    i2c.write(0x33, packet)


def _receiveLidarData(expectedCommand):
    # returns
    # success: boolean
    # data: none or bytearray 
    TIMEOUT = 1000
    MAX_SIZE = 32
    start_time = running_time()
    success = False
    data = None
    # find start of header
    started = False

    while running_time() - start_time < TIMEOUT and started == False:
        status = i2c.read(0x33, 1)[0] # status byte
        if status == 0x53: # success
            started = True
        elif status == 0x63: # fail, but as valid response
            return success, data
        sleep(16)

    if started == True:
        # read response header
        header = i2c.read(0x33, 3) # command and data length
        cmd = header[0]
        data_length = header[1] | (header[2] << 8)

        if cmd == expectedCommand:
            success = True
            data = bytearray()
            remaining_bytes = data_length
            chunk_size = min(remaining_bytes, MAX_SIZE)

            # read additional data if available
            while running_time() - start_time < TIMEOUT and remaining_bytes > 0:
                try:
                    chunk = i2c.read(0x33, chunk_size)
                    data.extend(chunk)
                    remaining_bytes -= len(chunk)
                except:
                    sleep(1)
    return success, data


def setLidarMode(mode=8):
    # mode: 8=8x8, 4=4x4 
    mode_text = "4x4" if mode == 4 else "8x8"
    print("Switching Lidar Mode to " + mode_text + ".\nPlease wait up to 10 seconds.")
    success = False

    for i in range(10):
        _sendLidarCommand(1, [0, 0, 0, mode])
        success, _ = _receiveLidarData(1)

        if success == True: break
        sleep(17)

    if success:
         sleep(5000) # WHY???
    else:
        raise RuntimeError("Failed to switch Lidar Mode")


def getDistanceAt(x_pos, y_pos):
    # pos: integer from 0 to 7, depending on mode
    # returns: integer, distance in cm
    _sendLidarCommand(0x3, [x_pos, y_pos])
    success, data = _receiveLidarData(0x3)
    if success and len(data) >= 2:
        distance = (data[0] | (data[1] << 8)) // 10
        return distance
    else:
        return 1023 # fail distance at 1023cm = 10m, TODO discuss desired value


# returns: list of all measured distances in cm
def getDistanceList():
    _sendLidarCommand(0x2)
    success, data = _receiveLidarData(0x2)
    if success and len(data) >= 32:
        distList = []
        for i in range(0,len(data),2):
            d = data[i] | (data[i+1] << 8)
            distList.append(d // 10)
        return distList
    else:
        return []


def getDistanceGrid():
    # returns: grid of all measured distances in cm
    _sendLidarCommand(0x2)
    success, data = _receiveLidarData(0x2)
    if success and len(data) >= 32:
        distGrid = []
        stride = 16 if len(data) == 128 else 8
        for i in range(0,len(data),stride):
            row = []
            for j in range(0,stride,2):
                d = data[i+j] | (data[i+j+1] << 8)
                row.append(d // 10)
            distGrid.append(row)
        return distGrid
    else:
        return []


def getDistanceRow(index):
    # returns: list of all distances from row at index.
    _sendLidarCommand(0x5, [index])
    success, data = _receiveLidarData(0x5)
    if success and len(data) >= 8:
        row = []
        for i in range(0, len(data), 2):
            distance = data[i] | (data[i+1] << 8)
            row.append(distance // 10)
        return row
    return []


def getDistanceColumn(index):
    # returns: list of all distances from column at index.
    _sendLidarCommand(0x6, [index])
    success, data = _receiveLidarData(0x6)
    if success and len(data) >= 8:
        col = []
        for i in range(0, len(data), 2):
            distance = data[i] | (data[i+1] << 8)
            col.append(distance // 10)
        return col
    return []


# TODO: Remove the following trash algorithms and do it youreself with raw sensor data!

def setObjectAvoidanceDistance(cm):
    _sendLidarCommand(8, [cm*10])
    succ, _ = _receiveLidarData(8)


def getObjectAvoidanceDirection():
    # only works with 4x4 mode via setLidarMode(4) beforehand
    # also set a limit via setObjectAvoidanceDistance(cm)
    # returns 1 number: 0=all_paths_blocked, -1=error, 1=go_left, 2=go_right, 3=go_straight
    _sendLidarCommand(6)
    succ, data = _receiveLidarData(6)
    if succ and len(data) >= 8:
        direction = data[0]
        blocked = data[1]
        # average distances
        average_distances_lmr = []
        for i in range(2, len(data), 2):
            dist = data[i] | (data[i+1] << 8)
            average_distances_lmr.append(dist//10)
        if blocked: 
            return 0
        else:
            return direction
    else:
        return -1