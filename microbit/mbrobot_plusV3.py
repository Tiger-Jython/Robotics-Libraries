# mbrobot_plusV3.py
# Date 25/11/25

from microbit import i2c, sleep, running_time, pin0, pin1, pin2
import neopixel
import music

_motorState = bytearray(5)
_speedPercent = 50
_powerByteL = 50
_powerByteR = 50
_powerBytesLUT = bytes(b'\x00\x0f\x10\x10\x11\x12\x12\x13\x13\x14\x15\x15\x16\x16\x17\x18\x18\x19\x19\x1a\x1b\x1b\x1c\x1c\x1d\x1e\x1e\x1f\x1f\x20\x21\x21\x22\x22\x23\x24\x24\x25\x25\x26\x27\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3b\x3c\x3e\x3f\x41\x43\x45\x47\x49\x4b\x4d\x50\x52\x55\x58\x5b\x5e\x61\x65\x69\x6d\x71\x75\x7a\x7f\x84\x89\x8f\x95\x9b\xa2\xa9\xb1\xb9\xc1\xca\xd3\xdd\xe8\xf3\xff')
_arcScaling = 0
_UNCONNECTEDERRORMSG = "Please connect to Maqueen robot and switch it on."
_underglowNP = neopixel.NeoPixel(pin1, 4)
_alarmSequence = ['c5:1', 'r', 'c5,1', 'r:3']
_buff1 = bytearray(1)
_buff2 = bytearray(2)
_add_mq = 0x10
_servoMinPulse=25
_servoMaxPulse=131
_lidarMode=8

def _wr1(reg):
    _buff1[0] = reg
    i2c.write(_add_mq, _buff1)

def _wr2(reg, val):
    _buff2[0] = reg
    _buff2[1] = val
    i2c.write(_add_mq, _buff2)

def _setMotors(dirL, powerL, dirR, powerR):
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
    _powerByteL = int(round(2.4*speed+14))
    _powerByteR = int(round(2.4*speed+14))

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

def _getPowerByteLUT(speed, offset):
    return min(_powerBytesLUT[speed] + offset, 255)

def _getArcBytes(r):
    rmm = int(r * 100)
    outerSpeed = _speedPercent
    if outerSpeed < 25:
        outerSpeed = 25
    reducedSpeed = 0
    if rmm > 5:
        n = outerSpeed * (3 * _arcScaling - outerSpeed - 9 * rmm + 220)
        d = -14 * _arcScaling + outerSpeed - 200 + 3 * outerSpeed - 10 * rmm - 290
        reducedSpeed = int(n/d)
        if reducedSpeed < 2:
            reducedSpeed = 2 if rmm > 15 else 1
    innerByte = _getPowerByteLUT(int(reducedSpeed), 0)
    outerByte = _getPowerByteLUT(int(outerSpeed), 0)
    return (innerByte, outerByte)

def rightArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, outer, 0, inner)


def leftArc(radius):
    inner, outer = _getArcBytes(radius)
    _setMotors(0, inner, 0, outer)

class Motor:
    def __init__(self, side):
        self._side = side

    def rotate(self, speed):
        speedClamped = int(min(max(abs(speed), 0), 100))
        power = speedClamped
        direction = 0 if speed > 0 else 1
        _setSingleMotor(self._side, direction, power)

def setServo(servo,angle):
    if angle < 0 or angle >180:
        raise ValueError("Invalid angle. Must be between 0 and 180")
    if servo in ["P0", "S1"]:
        pin = pin0
    elif servo in ["P1", "S2"]:
        pin = pin1
    elif servo in ["P2", "S3"]:
        pin = pin2
    else:
        raise ValueError("Valid servo names: S1, S2, S3 or P0, P1, P2")
    frac = (_servoMaxPulse - _servoMinPulse) * int(angle)
    offset = (frac >> 8)+ (frac >> 10) + (frac >> 11)+ (frac >> 12) # / 180
    usPulseTime = _servoMinPulse + offset 
    pin.set_analog_period(20)
    pin.write_analog(usPulseTime)
		
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
        return (byte & (2 ** self.index)) >> self.index

    def read_analog(self):
        try:
            _wr1(0x1D)
        except:
            raise RuntimeError(_UNCONNECTEDERRORMSG)
        buffer = i2c.read(0x10,11)
        return buffer[2+2*self.index] << 8 | buffer[1+2*self.index]

def setLEDs(rgbl, rgbr):
    _wr2(11, rgbl)
    _wr2(12, rgbr)

def setLED(rgb):
    setLEDs(rgb, rgb)
	
def setLEDLeft(rgbl):
    _wr2(11, rgbl)
	
def setLEDRight(rgbr):
    _wr2(12, rgbr)	

def fillRGB(red, green, blue):
    _underglowNP.clear()
    _underglowNP.fill((red,green,blue))
    _underglowNP.show()
	
def setRGB(r,g,b):
    fillRGB(r,g,b)
	
def clearRGB():
    _underglowNP.clear()

def posRGB(position, red, green, blue):
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

def readLightIntensity(side):
    _wr1(78)
    LightBuffer = i2c.read(0x10, 4, repeat=False)
    if side == 1:

        return LightBuffer[0] << 8 | LightBuffer[1]
    else:
        return LightBuffer[2] << 8 | LightBuffer[3]

def setPatrolSpeed(speed):
    _wr2(63, speed)

def setIntersectionRunMode(mode):
    _wr2(69, mode)

def setTRordRunMode(mode):
    _wr2(70, mode)

def setLeftOrStraightRunMode(mode):
    _wr2(71, mode)

def setRightOrStraightRunMode(mode):
    _wr2(72, mode)

def patrolling(patrol):
    if patrol == 1:
        val = 0x04 | 0x01
    else:
        val = 0x08
    _wr2(60, val)
   
def intersectionDetecting():
    _wr1(61)
    data = i2c.read(0x10, 1)[0]
    return data

def pidControlDistance(dir, distance, interruption):
    speed = 2
    if distance >= 6000:
        distance = 60000
    _wr2(64, dir)
    _wr2(85, speed)
    _wr2(65, distance >> 8)
    _wr2(66, distance)
    _wr2(60, 0x04 | 0x02)
    if (interruption == 1):
        _wr1(0x57)
        flagBuffer = i2c.read(0x10, 1)
        while flagBuffer[0] == 1:
            sleep(10)
            flagBuffer = i2c.read(0x10, 1)

def pidControlAngle(angle, interruption):
    speed = 2
    if angle >= 0:
        buf = 1
    else:
        buf = 2
        angle = -angle
    _wr2(67, buf)
    _wr2(86, speed)
    _wr2(68, angle)
    _wr2(60, 0x04 | 0x02)
    if interruption == 1:
        _wr1(0x57)
        buff = i2c.read(0x10, 1)
        while buff[0] == 1:
            sleep(10)
            buff = i2c.read(0x10, 1)

def pidControlStop():
    _wr2(60, 0x10)

def readRealTimeSpeed(type):
    _wr2(76, 1)
    buff = i2c.read(0x10, 2)
    if type == 1:
        return buff[0] / 5
    else:
        return buff[1] / 5

def _sendLidarCommand(cmd, args=[]):
    args_len = len(args)
    packet_len = args_len + 1 
    packet = bytearray(4 + args_len) 
    packet[0] = 0x55
    packet[1] = (packet_len >> 8) & 0xFF
    packet[2] = packet_len & 0xFF
    packet[3] = cmd
    for i, arg in enumerate(args):
        packet[4 + i] = arg
    # chunkwise sending? TODO
    i2c.write(0x33, packet)

def _receiveLidarData(expectedCommand):
    TIMEOUT = 1000
    MAX_SIZE = 32
    start_time = running_time()
    success = False
    data = None
    started = False

    while running_time() - start_time < TIMEOUT and started == False:
        status = i2c.read(0x33, 1)[0] 
        if status == 0x53: 
            started = True
        elif status == 0x63: 
            return success, data
        sleep(16)

    if started == True:
        header = i2c.read(0x33, 3) 
        cmd = header[0]
        data_length = header[1] | (header[2] << 8)

        if cmd == expectedCommand:
            success = True
            data = bytearray()
            remaining_bytes = data_length
            chunk_size = min(remaining_bytes, MAX_SIZE)
            while running_time() - start_time < TIMEOUT and remaining_bytes > 0:
                try:
                    chunk = i2c.read(0x33, chunk_size)
                    data.extend(chunk)
                    remaining_bytes -= len(chunk)
                except:
                    sleep(1)
    return success, data

def setLidarMode(mode=8):
    global _lidarMode
    if 4 != mode or 8!=mode:
        raise ValueError("Lidar mode must be 4 or 8")
    mode_text = "4x4" if mode == 4 else "8x8"
    print("Switching Lidar Mode to " + mode_text + ".\nPlease wait up to 10 seconds.")
    success = False

    for i in range(10):
        _sendLidarCommand(1, [0, 0, 0, mode])
        success, _ = _receiveLidarData(1)

        if success == True: break
        sleep(17)

    if success:
        _lidarMode = mode
        sleep(5000)
    else:
        raise RuntimeError("Failed to switch Lidar Mode")

def getDistanceAt(x_pos, y_pos):
    _sendLidarCommand(0x3, [x_pos, y_pos])
    success, data = _receiveLidarData(0x3)
    if success and len(data) >= 2:
        distance = (data[0] | (data[1] << 8)) // 10
        return distance
    else:
        return 1023

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

def getDistance():
    global _lidarMode
    mid = _lidarMode/2
    topLeft = getDistanceAt(mid-1, mid-1)
    topRight = getDistanceAt(mid, mid-1)
    bottomLeft = getDistanceAt(mid-1, mid)
    bottomRight = getDistanceAt(mid, mid)
    distanceList = [topLeft, topRight, bottomLeft, bottomRight]
    return min(distanceList)

		
def getDistanceGrid():
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
    _sendLidarCommand(0x6, [index])
    success, data = _receiveLidarData(0x6)
    if success and len(data) >= 8:
        col = []
        for i in range(0, len(data), 2):
            distance = data[i] | (data[i+1] << 8)
            col.append(distance // 10)
        return col
    return []
    
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