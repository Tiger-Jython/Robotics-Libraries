_B=True
_A=False
from microbit import i2c,sleep,running_time,pin0,pin1,pin2
import neopixel,music
_g1=bytearray(5)
_g2=50
_g3=50
_g4=50
_g5=bytes(b'\x00\x0f\x10\x10\x11\x12\x12\x13\x13\x14\x15\x15\x16\x16\x17\x18\x18\x19\x19\x1a\x1b\x1b\x1c\x1c\x1d\x1e\x1e\x1f\x1f !!""#$$%%&\')*+,-./0123456789:;;<>?ACEGIKMPRUX[^aeimquz\x7f\x84\x89\x8f\x95\x9b\xa2\xa9\xb1\xb9\xc1\xca\xd3\xdd\xe8\xf3\xff')
_g6=0
_g7='Please connect to Maqueen robot and switch it on.'
_g8=neopixel.NeoPixel(pin1,4)
_g9=['c5:1','r','c5,1','r:3']
_g10=bytearray(1)
_g11=bytearray(2)
_g12=16
_g13=25
_g14=131
_g15=8
def _f1(reg):_g10[0]=reg;i2c.write(_g12,_g10)
def _f2(reg,val):_g11[0]=reg;_g11[1]=val;i2c.write(_g12,_g11)
def _f3(dirL,powerL,dirR,powerR):
	global _g1;_g1[1]=dirL;_g1[2]=powerL;_g1[3]=dirR;_g1[4]=powerR
	try:i2c.write(16,_g1)
	except:raise RuntimeError(_g7)
def _f4(side,dir,power):
	global _g1;_g1[1+side]=dir;_g1[2+side]=power
	try:i2c.write(16,_g1)
	except:raise RuntimeError(_g7)
def setSpeed(speed):A=speed;global _g2;global _g3;global _g4;_g2=int(min(max(A,0),100));_g3=int(round(2.4*A+14));_g4=int(round(2.4*A+14))
def resetSpeed():setSpeed(50)
def stop():_f3(0,0,0,0)
def forward():_f3(0,_g3,0,_g4)
def backward():_f3(1,_g3,1,_g4)
def left():_f3(1,_g3,0,_g4)
def right():_f3(0,_g3,1,_g4)
def _f5(speed,offset):return min(_g5[speed]+offset,255)
def _f6(r):
	B=int(r*100);A=_g2
	if A<25:A=25
	C=0
	if B>5:
		D=A*(3*_g6-A-9*B+220);E=-14*_g6+A-200+3*A-10*B-290;C=int(D/E)
		if C<2:C=2 if B>15 else 1
	F=_f5(int(C),0);G=_f5(int(A),0);return F,G
def rightArc(radius):A,B=_f6(radius);_f3(0,B,0,A)
def leftArc(radius):A,B=_f6(radius);_f3(0,A,0,B)
class Motor:
	def __init__(A,side):A._side=side
	def rotate(B,speed):A=speed;C=int(min(max(abs(A),0),100));D=C;E=0 if A>0 else 1;_f4(B._side,E,D)
def setServo(servo,angle):
	D=angle;C=servo
	if D<0 or D>180:raise ValueError('Invalid angle. Must be between 0 and 180')
	if C in['P0','S1']:A=pin0
	elif C in['P1','S2']:A=pin1
	elif C in['P2','S3']:A=pin2
	else:raise ValueError('Valid servo names: S1, S2, S3 or P0, P1, P2')
	B=(_g14-_g13)*int(D);E=(B>>8)+(B>>10)+(B>>11)+(B>>12);F=_g13+E;A.set_analog_period(20);A.write_analog(F)
class IRSensor:
	_g19=bytes(b'\x1d')
	def __init__(A,index):A.index=index
	def read_digital(A):
		try:i2c.write(16,IRSensor._g19)
		except:raise RuntimeError(_g7)
		B=~i2c.read(16,1)[0];return(B&2**A.index)>>A.index
	def read_analog(A):
		try:_f1(29)
		except:raise RuntimeError(_g7)
		B=i2c.read(16,11);return B[2+2*A.index]<<8|B[1+2*A.index]
def setLEDs(rgbl,rgbr):_f2(11,rgbl);_f2(12,rgbr)
def setLED(rgb):setLEDs(rgb,rgb)
def setLEDLeft(rgbl):_f2(11,rgbl)
def setLEDRight(rgbr):_f2(12,rgbr)
def fillRGB(red,green,blue):_g8.clear();_g8.fill((red,green,blue));_g8.show()
def setRGB(r,g,b):fillRGB(r,g,b)
def clearRGB():_g8.clear()
def posRGB(position,red,green,blue):
	A=position
	if A<0 or A>3:raise ValueError('invalid RGB-LED position. Must be 0,1,2 or 3.')
	_g8[A]=red,green,blue;_g8.show()
def setAlarm(state):
	if state:music.play(_g9,wait=_A,loop=_B)
	else:music.stop()
def beep():music.pitch(440,200,wait=_A)
def readLightIntensity(side):
	_f1(78);A=i2c.read(16,4,repeat=_A)
	if side==1:return A[0]<<8|A[1]
	else:return A[2]<<8|A[3]
def setPatrolSpeed(speed):_f2(63,speed)
def setIntersectionRunMode(mode):_f2(69,mode)
def setTRordRunMode(mode):_f2(70,mode)
def setLeftOrStraightRunMode(mode):_f2(71,mode)
def setRightOrStraightRunMode(mode):_f2(72,mode)
def patrolling(patrol):
	if patrol==1:A=5
	else:A=8
	_f2(60,A)
def intersectionDetecting():_f1(61);A=i2c.read(16,1)[0];return A
def pidControlDistance(dir,distance,interruption):
	A=distance;C=2
	if A>=6000:A=60000
	_f2(64,dir);_f2(85,C);_f2(65,A>>8);_f2(66,A);_f2(60,6)
	if interruption==1:
		_f1(87);B=i2c.read(16,1)
		while B[0]==1:sleep(10);B=i2c.read(16,1)
def pidControlAngle(angle,interruption):
	A=angle;D=2
	if A>=0:B=1
	else:B=2;A=-A
	_f2(67,B);_f2(86,D);_f2(68,A);_f2(60,6)
	if interruption==1:
		_f1(87);C=i2c.read(16,1)
		while C[0]==1:sleep(10);C=i2c.read(16,1)
def pidControlStop():_f2(60,16)
def readRealTimeSpeed(type):
	_f2(76,1);A=i2c.read(16,2)
	if type==1:return A[0]/5
	else:return A[1]/5
def _f7(cmd,args=[]):
	B=len(args);C=B+1;A=bytearray(4+B);A[0]=85;A[1]=C>>8&255;A[2]=C&255;A[3]=cmd
	for(D,E)in enumerate(args):A[4+D]=E
	i2c.write(51,A)
def _f8(expectedCommand):
	F=1000;J=32;G=running_time();B=_A;A=None;C=_A
	while running_time()-G<F and C==_A:
		H=i2c.read(51,1)[0]
		if H==83:C=_B
		elif H==99:return B,A
		sleep(16)
	if C==_B:
		D=i2c.read(51,3);K=D[0];L=D[1]|D[2]<<8
		if K==expectedCommand:
			B=_B;A=bytearray();E=L;M=min(E,J)
			while running_time()-G<F and E>0:
				try:I=i2c.read(51,M);A.extend(I);E-=len(I)
				except:sleep(1)
	return B,A
def setLidarMode(mode=8):
	A=mode;global _g15;C=str(A)+'x'+str(A);print('Switching Lidar Mode to '+C+'.\nPlease wait up to 10 seconds.');B=_A
	for D in range(10):
		_f7(1,[0,0,0,A]);B,E=_f8(1)
		if B==_B:break
		sleep(17)
	if B:_g15=A;sleep(5000)
	else:raise RuntimeError('Failed to switch Lidar Mode')
def getDistanceAt(x_pos,y_pos):
	_f7(3,[x_pos,y_pos]);B,A=_f8(3)
	if B and len(A)>=2:C=(A[0]|A[1]<<8)//10;return C
	else:return 1023
def getDistanceList():
	_f7(2);D,A=_f8(2)
	if D and len(A)>=32:
		B=[]
		for C in range(0,len(A),2):E=A[C]|A[C+1]<<8;B.append(E//10)
		return B
	else:return[]
def getDistance():global _g15;A=_g15/2;B=getDistanceAt(A-1,A-1);C=getDistanceAt(A,A-1);D=getDistanceAt(A-1,A);E=getDistanceAt(A,A);F=[B,C,D,E];return min(F)
def getDistanceGrid():
	_f7(2);G,A=_f8(2)
	if G and len(A)>=32:
		B=[];C=16 if len(A)==128 else 8
		for D in range(0,len(A),C):
			E=[]
			for F in range(0,C,2):H=A[D+F]|A[D+F+1]<<8;E.append(H//10)
			B.append(E)
		return B
	else:return[]
def getDistanceRow(index):
	_f7(5,[index]);D,A=_f8(5)
	if D and len(A)>=8:
		B=[]
		for C in range(0,len(A),2):E=A[C]|A[C+1]<<8;B.append(E//10)
		return B
	return[]
def getDistanceColumn(index):
	_f7(6,[index]);D,A=_f8(6)
	if D and len(A)>=8:
		B=[]
		for C in range(0,len(A),2):E=A[C]|A[C+1]<<8;B.append(E//10)
		return B
	return[]
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