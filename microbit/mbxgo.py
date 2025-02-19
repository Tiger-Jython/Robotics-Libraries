from microbit import *

_speed = 50
_XGOInit = False
_TX = pin14
_RX = pin13


def checkInit(func):
    def wrapper(*args, **kwargs):
        global _XGOInit
        if not _XGOInit:
            init_xgo_serial(_TX, _RX)
        return func(*args, **kwargs)
    return wrapper


def _map(speed, in_min, in_max, out_min, out_max):
    return (speed - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


@checkInit
def _move(direction, speed):
    move_buffer = bytearray(9)
    move_buffer[0] = 0x55
    move_buffer[1] = 0x00
    move_buffer[2] = 0x09
    move_buffer[3] = 0x00
    move_buffer[7] = 0x00
    move_buffer[8] = 0xAA

    speed = max(0, min(100, speed))

    if direction == 0:
        move_buffer[4] = 0x30
        move_buffer[5] = _map(speed, 0, 100, 128, 255)
    elif direction == 1:
        move_buffer[4] = 0x30
        move_buffer[5] = _map(speed, 0, 100, 128, 0)
    elif direction == 2:
        move_buffer[4] = 0x31
        move_buffer[5] = _map(speed, 0, 100, 128, 0)
    elif direction == 3:
        move_buffer[4] = 0x31
        move_buffer[5] = _map(speed, 0, 100, 128, 255)

    move_buffer[6] = ~(0x09 + 0x00 + move_buffer[4] + move_buffer[5]) & 0xFF

    uart.write(move_buffer)


@checkInit
def clampX(milimeters=50):
    clampBuffer = bytearray(9)
    clampBuffer[0] = 0x55
    clampBuffer[1] = 0x00
    clampBuffer[2] = 0x09
    clampBuffer[3] = 0x00
    clampBuffer[4] = 0x73
    clampBuffer[7] = 0x00
    clampBuffer[8] = 0xAA

    clampBuffer[5] = milimeters
    clampBuffer[6] = ~(0x09 + 0x00 + 0x73 + clampBuffer[5]) & 0xFF

    uart.write(clampBuffer)
    sleep(1000)


@checkInit
def clampZ(milimeters=50):
    clampBuffer = bytearray(9)
    clampBuffer[0] = 0x55
    clampBuffer[1] = 0x00
    clampBuffer[2] = 0x09
    clampBuffer[3] = 0x00
    clampBuffer[4] = 0x74
    clampBuffer[7] = 0x00
    clampBuffer[8] = 0xAA

    clampBuffer[5] = milimeters
    clampBuffer[6] = ~(0x09 + 0x00 + 0x74 + clampBuffer[5]) & 0xFF

    uart.write(clampBuffer)
    sleep(1000)


@checkInit
def clamp(force):
    clampBuffer = bytearray(9)
    clampBuffer[0] = 0x55
    clampBuffer[1] = 0x00
    clampBuffer[2] = 0x09
    clampBuffer[3] = 0x00
    clampBuffer[4] = 0x71
    clampBuffer[7] = 0x00
    clampBuffer[8] = 0xAA

    clampBuffer[5] = force
    clampBuffer[6] = ~(0x09 + 0x00 + 0x71 + clampBuffer[5]) & 0xFF

    uart.write(clampBuffer)
    sleep(1000)


def init_xgo_serial(tx_pin, rx_pin, baudrate=115200):
    global _XGOInit
    uart.init(baudrate=baudrate, tx=tx_pin, rx=rx_pin)
    init_action()
    _XGOInit = True


def init_action():
    commands_buffer = bytearray(9)
    commands_buffer[0] = 0x55
    commands_buffer[1] = 0x00
    commands_buffer[2] = 0x09
    commands_buffer[3] = 0x00
    commands_buffer[4] = 0x3E
    commands_buffer[5] = 0xFF
    commands_buffer[6] = ~(0x09 + 0x00 + 0x3E + 0xFF) & 0xFF
    commands_buffer[7] = 0x00
    commands_buffer[8] = 0xAA

    uart.write(commands_buffer)
    sleep(2000)


@checkInit
def action(id):
    commands_buffer = bytearray(9)
    commands_buffer[0] = 0x55
    commands_buffer[1] = 0x00
    commands_buffer[2] = 0x09
    commands_buffer[3] = 0x00
    commands_buffer[4] = 0x3E
    commands_buffer[5] = id
    commands_buffer[6] = ~(0x09 + 0x00 + 0x3E + id) & 0xFF
    commands_buffer[7] = 0x00
    commands_buffer[8] = 0xAA

    uart.write(commands_buffer)
    sleep(2000)


def changeInit(tx, rx):
    global _TX
    global _RX
    _TX = tx
    _RX = rx
    init_xgo_serial(_TX, _RX)


@checkInit
def setSpeed(speed):
    global _speed
    _speed = speed


def forward():
    _move(0, _speed)


def backward():
    _move(1, _speed)


def left():
    _move(2, _speed)


def right():
    _move(3, _speed)
