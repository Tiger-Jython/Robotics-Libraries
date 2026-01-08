from microbit import i2c,pin0,pin1,pin2,pin13,pin14,pin15,sleep
import gc,machine,music,neopixel
_g1=50
_g2=50
_g3=50
_g4=bytearray(5)
_g5=bytes(b'\x00\x0f\x10\x10\x11\x12\x12\x13\x13\x14\x15\x15\x16\x16\x17\x18\x18\x19\x19\x1a\x1b\x1b\x1c\x1c\x1d\x1e\x1e\x1f\x1f !!""#$$%%&\')*+,-./0123456789:;;<>?ACEGIKMPRUX[^aeimquz\x7f\x84\x89\x8f\x95\x9b\xa2\xa9\xb1\xb9\xc1\xca\xd3\xdd\xe8\xf3\xff')
_g6=0
_g7=0
_g8=0
_g9=25
_g10=131
_g11=bytearray(b'\x0b\x00\x00')
_g12=neopixel.NeoPixel(pin15,4)
np_rgb_pixels=_g12
_g13=['c5:1','r','c5,1','r:3']
_g14='Please connect to Maqueen robot and switch it on.'
def _f1(dirL,powerL,dirR,powerR):
	global _g4;_g4[1]=dirL;_g4[2]=powerL;_g4[3]=dirR;_g4[4]=powerR
	try:i2c.write(16,_g4)
	except:raise RuntimeError(_g14)
def _f2(side,dir,power):
	global _g4;_g4[1+side]=dir;_g4[2+side]=power
	try:i2c.write(16,_g4)
	except:raise RuntimeError(_g14)
def _f3(speed,offset):return min(_g5[speed]+offset,255)
def _f4(r):
	B=int(r*100);A=_g1
	if A<25:A=25
	H=min(abs(A-70),20)/20;C=0
	if B>5:
		D=A*(3*_g8-A-9*B+220);E=-14*_g8+A-200+3*A-10*B-290;C=int(D/E)
		if C<2:C=2 if B>15 else 1
	F=_f3(int(C),0);G=_f3(int(A),0);return F,G
def calibrate(offset,differential=0,arcScaling=0):global _g7;global _g6;global _g8;_g6=max(min(int(offset),50),-14);_g7=max(min(int(differential),150),-150);_g8=max(min(arcScaling,50),-50);setSpeed(_g1)
def setSpeed(speed):
	global _g1;global _g2;global _g3;_g1=int(min(max(speed,0),100));A=_f3(_g1,_g6);B=round((1-_g1/100)*abs(_g7))if _g1>0 else 0;C=round(_g1/100*abs(_g7))
	if _g7>0:_g2=A-C;_g3=A+B
	else:_g2=A+B;_g3=A-C
def resetSpeed():setSpeed(50)
def stop():_f1(0,0,0,0)
def forward():_f1(0,_g2,0,_g3)
def backward():_f1(1,_g2,1,_g3)
def left():_f1(1,_g2,0,_g3)
def right():_f1(0,_g2,1,_g3)
def rightArc(radius):A,B=_f4(radius);_f1(0,B,0,A)
def leftArc(radius):A,B=_f4(radius);_f1(0,A,0,B)
class Motor:
	def __init__(A,side):A._side=side
	def rotate(B,speed):A=speed;C=int(min(max(abs(A),0),100));D=_f3(C,_g6);E=0 if A>0 else 1;_f2(B._side,E,D)
def setServo(servo,angle):
	D=angle;A=servo
	if A=='P0'or A=='S1':B=pin0
	elif A=='P1'or A=='S2':B=pin1
	elif A=='P2':B=pin2
	else:raise ValueError("Unknown Servo. Please use 'P0', 'P1' or 'P2'.")
	if D<0 or D>180:raise ValueError('Invalid angle. Must be between 0 and 180')
	C=(_g10-_g9)*int(D);E=(C>>8)+(C>>10)+(C>>11)+(C>>12);F=_g9+E;B.set_analog_period(20);B.write_analog(F)
def setMinAngleVal(duty):global _g9;_g9=int(duty)
def setMaxAngleVal(duty):global _g10;_g10=int(duty)
class IRSensor:
	_g21=bytes(b'\x1d')
	def __init__(A,index):A._index=index
	def read_digital(A):
		try:i2c.write(16,IRSensor._g21)
		except:raise RuntimeError(_g14)
		B=~i2c.read(16,1)[0];return(B&2**A._index)>>A._index
	def read_analog(A):
		try:i2c.write(16,IRSensor._g21)
		except:raise RuntimeError(_g14)
		B=i2c.read(16,11);return B[1+A._index*2]
def ir_read_values_as_byte():i2c.write(16,bytearray([29]));A=i2c.read(16,1);return~A[0]
def getDistance():pin13.write_digital(1);pin13.write_digital(0);A=machine.time_pulse_us(pin14,1,50000);B=(A>>6)+(A>>10)+(A>>11)+(A>>12)+1;return max(min(B,500),0)if B>0 else 255
def setLED(state,stateR=None):B=state;A=stateR;global _g11;A=A if A!=None else B;_g11[1]=B;_g11[2]=A;i2c.write(16,_g11)
def setLEDLeft(state):global _g11;_g11[1]=state;i2c.write(16,_g11)
def setLEDRight(state):global _g11;_g11[2]=state;i2c.write(16,_g11)
def fillRGB(red,green,blue):
	for A in range(4):_g12[A]=red,green,blue
	_g12.show()
setRGB=fillRGB
def clearRGB():_g12.clear()
def posRGB(position,red,green,blue):
	A=position
	if A<0 or A>3:raise ValueError('invalid RGB-LED position. Must be 0,1,2 or 3.')
	_g12[A]=red,green,blue;_g12.show()
def setAlarm(state):
	if state:music.play(_g13,wait=False,loop=True)
	else:music.stop()
def beep():music.pitch(440,200,wait=False)
class LEDState:ON=1;OFF=0;RED=1
class IR:R2=0;R1=1;M=2;L1=3;L2=4;masks=[1,2,4,8,16]
pin2.set_pull(pin2.NO_PULL)
delay=sleep
irR2=IRSensor(0)
irR1=IRSensor(1)
irRight=irR1
irM=IRSensor(2)
irL1=IRSensor(3)
irLeft=irL1
irL2=IRSensor(4)
motL=Motor(0)
motR=Motor(2)