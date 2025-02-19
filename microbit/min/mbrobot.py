from microbit import i2c,pin1,pin2,pin8,pin12,pin13,pin14,pin15,sleep
import gc,machine,music,neopixel
_g1=50
_g2=40
_g3=40
_g4=bytearray(5)
_g5=bytearray(2)
_g6=bytes(b'\x00\x0b\x0b\x0c\x0c\r\r\r\x0e\x0e\x0f\x0f\x0f\x10\x10\x11\x11\x11\x12\x12\x13\x13\x13\x14\x14\x15\x15\x15\x16\x16\x17\x17\x17\x18\x19\x1a\x1b\x1b\x1c\x1d\x1e\x1f !"##$%&\'()*++,-./0123468:<?ADFILOSVZ^bgkpu{\x81\x87\x8d\x94\x9b\xa3\xab\xb4\xbd\xc6\xd0\xdb\xe6\xf2\xff')
_g7=0
_g8=0
_g9=0
_g10=neopixel.NeoPixel(pin15,4)
np_rgb_pixels=_g10
_g11=['c5:1','r','c5:1','r:3']
_g12='Please connect to Maqueen robot and switch it on.'
def _f1(dirL,powerL,dirR,powerR):
	global _g4;_g4[1]=dirL;_g4[2]=powerL;_g4[3]=dirR;_g4[4]=powerR
	try:i2c.write(16,_g4)
	except:raise RuntimeError(_g12)
def _f2(side,dir,power):
	global _g4;_g4[1+side]=dir;_g4[2+side]=power
	try:i2c.write(16,_g4)
	except:raise RuntimeError(_g12)
def _f3(speed,offset):return min(_g6[speed]+offset,255)
def _f4(r):
	A=_g1;B=int(r*100);D=A-max(B+20,40)
	if D<=0:A=min(max(B+40,40),100)
	C=0
	if B>=4:E=(100-A)//2;C=(B*10-35)/(B*(11+(_g9-4)/10)+90+E);C=C*A
	F=_f3(int(C),0);G=_f3(int(A),0);return F,G
def calibrate(offset,differential=0,arcScaling=0):global _g8;global _g7;global _g9;_g7=max(min(int(offset),50),-10);_g8=max(min(int(differential),150),-150);_g9=max(min(arcScaling,50),-15);setSpeed(_g1)
def setSpeed(speed):
	global _g1;global _g2;global _g3;_g1=int(min(max(speed,0),100));A=_f3(_g1,_g7);B=round((1-_g1/100)*abs(_g8))if _g1>0 else 0;C=round(_g1/100*abs(_g8))
	if _g8>0:_g2=A-C;_g3=A+B
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
	def rotate(B,speed):A=speed;C=int(min(max(abs(A),0),100));D=_f3(C,_g7);E=0 if A>0 else 1;_f2(B._side,E,D)
def setServo(servo,angle):
	B=angle;A=servo;global _g5
	if A=='S1'or A=='P0':_g5[0]=20
	elif A=='S2'or A=='P1':_g5[0]=21
	else:raise ValueError("Unknown Servo. Please use 'S1' or 'S2'.")
	if B<0 or B>180:raise ValueError('Invalid angle. Must be between 0 and 180')
	_g5[1]=B
	try:i2c.write(16,_g5)
	except:raise RuntimeError(_g12)
class IRSensor:
	def __init__(A,pin):A._pin=pin
	def read_digital(A):return A._pin.read_digital()
	def read_analog(A):raise NameError('Maqueen Lite does not support reading analog sensor values.')
def getDistance():pin1.write_digital(1);pin1.write_digital(0);A=machine.time_pulse_us(pin2,1,50000);B=(A>>6)+(A>>10)+(A>>11)+(A>>12)+1;return max(min(B,500),0)if B>0 else 255
def setLED(state,stateR=None):B=state;A=stateR;A=A if A!=None else B;pin8.write_digital(B);pin12.write_digital(A)
def setLEDLeft(state):pin8.write_digital(state)
def setLEDRight(state):pin12.write_digital(state)
def fillRGB(red,green,blue):
	for A in range(4):_g10[A]=red,green,blue
	_g10.show()
def clearRGB():_g10.clear()
def setRGB(position,red,green,blue):
	A=position
	if A<0 or A>3:raise ValueError('invalid RGB-LED position. Must be 0,1,2 or 3.')
	_g10[A]=red,green,blue;_g10.show()
def setAlarm(state):
	if state:music.play(_g11,wait=False,loop=True)
	else:music.stop()
def beep():music.pitch(440,200,wait=False)
pin2.set_pull(pin2.NO_PULL)
delay=sleep
irLeft=IRSensor(pin13)
irRight=IRSensor(pin14)
motL=Motor(0)
motR=Motor(2)