# callimk.py (motionkit2)
import gc
from calliope_mini import i2c, sleep
i2c.init()
_v = 30
_axe = 0.09


def w(d1, d2, s1, s2):
    i2c.write(0x10, bytearray([0x00, d1, s1]))
    i2c.write(0x10, bytearray([0x02, d2, s2]))


def forward():
    w(0, 0, _v, _v)


def backward():
    w(1, 1, _v, _v)


def stop():
    w(0, 0, 0, 0)


def right():
    w(0 if _v > 0 else 1, 1 if _v > 0 else 0, _v, _v)


def left():
    w(1 if _v > 0 else 0, 0 if _v > 0 else 1, _v, _v)


def rightArc(r):
    v = abs(_v)
    if r < _axe:
        v1 = 0
    else:
        f = (r - _axe) / (r + _axe) * (1 - v * v / 200000)
        v1 = int(f * v)
    if _v > 0:
        w(0, 0, v, v1)
    else:
        w(1, 1, v1, v)


def leftArc(r):
    v = abs(_v)
    if r < _axe:
        v1 = 0
    else:
        f = (r - _axe) / (r + _axe) * (1 - v * v / 200000)
        v1 = int(f * v)
    if _v > 0:
        w(0, 0, v1, v)
    else:
        w(1, 1, v, v1)


def setSpeed(speed):
    global _v
    if speed < 15:
        _v = 15
    else:
        _v = speed


def motorL(dir, speed):
    i2c.write(0x10, bytearray([0x00, dir, speed]))


def motorR(dir, speed):
    i2c.write(0x10, bytearray([0x02, dir, speed]))


def led(right_left, on_off):
    buf_led = bytearray(2)
    if right_left == 0:
        buf_led[0] = 0x0B
    else:
        buf_led[0] = 0x0C
    buf_led[1] = on_off
    i2c.write(0x10, buf_led)


def setLEDLeft(on):
    led(1, on)


def setLEDRight(on):
    led(0, on)


def setLED(on):
    led(1, on)
    led(0, on)


def rgbLED(red, green, blue):
    buf_rgbLed_red = bytearray(2)
    buf_rgbLed_red[0] = 0x18
    buf_rgbLed_red[1] = red
    buf_rgbLed_green = bytearray(2)
    buf_rgbLed_green[0] = 0x19
    buf_rgbLed_green[1] = green
    buf_rgbLed_blue = bytearray(2)
    buf_rgbLed_blue[0] = 0x1A
    buf_rgbLed_blue[1] = blue
    i2c.write(0x10, buf_rgbLed_red)
    i2c.write(0x10, buf_rgbLed_green)
    i2c.write(0x10, buf_rgbLed_blue)


def getDistance():
    i2c.write(0x10, bytearray([0x28]))
    sleep(20)
    data = i2c.read(0x10, 2)
    distance = (data[0] << 8) | data[1]
    return distance


def irLeftValue():
    i2c.write(0x10, bytearray([0x1D]))
    data = i2c.read(0x10, 1)[0]
    return 0 if (data & 0x01) != 0 else 1


def irRightValue():
    i2c.write(0x10, bytearray([0x1D]))
    data = i2c.read(0x10, 1)[0]
    return 0 if (data & 0x02) != 0 else 1


def setServo(S, Angle):
    if S == "S1":
        Servo = 0x14
    if S == "S2":
        Servo = 0x15
    i2c.write(0x10, bytearray([Servo, Angle]))


exit = stop
delay = sleep
