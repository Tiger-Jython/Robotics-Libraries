_B=True
_A=False
from microbit import i2c,sleep,running_time,pin2,pin1
import neopixel,music
_g1=bytearray(5)
_g2=50
_g3=50
_g4=50
_g5=0
_g6='Please connect to Maqueen robot and switch it on.'
_g7=neopixel.NeoPixel(pin1,4)
_g8=['c5:1','r','c5,1','r:3']
_g9=bytearray(1)
_g10=bytearray(2)
_g11=16
def _f1(reg):_g9[0]=reg;i2c.write(_g11,_g9)
def _f2(reg,val):_g10[0]=reg;_g10[1]=val;i2c.write(_g11,_g10)
def _f3(dirL,powerL,dirR,powerR):
	global _g1;_g1[1]=dirL;_g1[2]=powerL;_g1[3]=dirR;_g1[4]=powerR
	try:i2c.write(16,_g1)
	except:raise RuntimeError(_g6)
def _f4(side,dir,power):
	global _g1;_g1[1+side]=dir;_g1[2+side]=power
	try:i2c.write(16,_g1)
	except:raise RuntimeError(_g6)
def setSpeed(speed):A=speed;global _g2;global _g3;global _g4;_g2=int(min(max(A,0),100));_g3=int(round(2.4*A+14));_g4=int(round(2.4*A+14))
def resetSpeed():setSpeed(50)
def stop():_f3(0,0,0,0)
def forward():_f3(0,_g3,0,_g4)
def backward():_f3(1,_g3,1,_g4)
def left():_f3(1,_g3,0,_g4)
def right():_f3(0,_g3,1,_g4)
def _f5(r):
	C=int(r*100);A=_g2
	if A<25:A=25
	B=0
	if C>5:
		E=A*(3*_g5-A-9*C+220);D=-14*_g5+A-200+3*A-10*C-290
		if D!=0:B=int(E/D)
		if B<2:B=2 if C>15 else 1
	if B<0:B=0
	if B>255:B=255
	if A>255:A=255
	return int(B),int(A)
def rightArc(radius):A,B=_f5(radius);_f3(0,B,0,A)
def leftArc(radius):A,B=_f5(radius);_f3(0,A,0,B)
class Motor:
	def __init__(A,side):A._side=side
	def rotate(B,speed):A=speed;C=int(min(max(abs(A),0),100));D=C;E=0 if A>0 else 1;_f4(B._side,E,D)
class IRSensor:
	_g15=bytes(b'\x1d')
	def __init__(A,index):A.index=index
	def read_digital(A):
		try:i2c.write(16,IRSensor._g15)
		except:raise RuntimeError(_g6)
		B=~i2c.read(16,1)[0];return(B&2**A.index)>>A.index
	def read_analog(A):
		try:_f1(29)
		except:raise RuntimeError(_g6)
		B=i2c.read(16,11);return B[2+2*A.index]<<8|B[1+2*A.index]
def setLEDs(rgbl,rgbr):_f2(11,rgbl);_f2(12,rgbr)
def setLED(rgb):setLEDs(rgb,rgb)
def setLEDLeft(rgbl):_f2(11,rgbl)
def setLEDRight(rgbr):_f2(12,rgbr)
def fillRGB(red,green,blue):_g7.fill((red,green,blue));_g7.show()
def clearRGB():_g7.clear()
def setRGB(position,red,green,blue):
	A=position
	if A<0 or A>3:raise ValueError('invalid RGB-LED position. Must be 0,1,2 or 3.')
	_g7[A]=red,green,blue;_g7.show()
def setAlarm(state):
	if state:music.play(_g8,wait=_A,loop=_B)
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
def _f6(cmd,args=[]):
	B=len(args);C=B+1;A=bytearray(4+B);A[0]=85;A[1]=C>>8&255;A[2]=C&255;A[3]=cmd
	for(D,E)in enumerate(args):A[4+D]=E
	i2c.write(51,A)
def _f7(expectedCommand):
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
	B='4x4'if mode==4 else'8x8';print('Switching Lidar Mode to '+B+'.\nPlease wait up to 10 seconds.');A=_A
	for C in range(10):
		_f6(1,[0,0,0,mode]);A,D=_f7(1)
		if A==_B:break
		sleep(17)
	if A:sleep(5000)
	else:raise RuntimeError('Failed to switch Lidar Mode')
def getDistanceAt(x_pos,y_pos):
	_f6(3,[x_pos,y_pos]);B,A=_f7(3)
	if B and len(A)>=2:C=(A[0]|A[1]<<8)//10;return C
	else:return 1023
def getDistanceList():
	_f6(2);D,A=_f7(2)
	if D and len(A)>=32:
		B=[]
		for C in range(0,len(A),2):E=A[C]|A[C+1]<<8;B.append(E//10)
		return B
	else:return[]
def getDistanceGrid():
	_f6(2);G,A=_f7(2)
	if G and len(A)>=32:
		B=[];C=16 if len(A)==128 else 8
		for D in range(0,len(A),C):
			E=[]
			for F in range(0,C,2):H=A[D+F]|A[D+F+1]<<8;E.append(H//10)
			B.append(E)
		return B
	else:return[]
def getDistanceRow(index):
	_f6(5,[index]);D,A=_f7(5)
	if D and len(A)>=8:
		B=[]
		for C in range(0,len(A),2):E=A[C]|A[C+1]<<8;B.append(E//10)
		return B
	return[]
def getDistanceColumn(index):
	_f6(6,[index]);D,A=_f7(6)
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