_A='Please switch on mbRobot!'
from microbit import i2c,pin0,pin1,pin2,sleep
import machine,gc,music
_g1=50
_g2=.082
def w(d1,d2,s1,s2):
	try:i2c.write(16,bytearray([0,d1,d2,s1,s2]))
	except:print(_A)
def setSpeed(speed):
	A=speed;global _g1
	if A<30 and A!=0:setPID(1);_g1=A+30
	elif A>=30 and A<32:setPID(0);_g1=A+2
	else:setPID(0);_g1=A
def setPID(pd):i2c.write(16,bytearray([10,pd]))
def stop():setPID(0);w(0,0,0,0)
def resetSpeed():setPID(0);A=50
def forward():w(1,_g1,1,_g1)
def backward():w(2,_g1,2,_g1)
def left():A=1.825-.0175*_g1;w(2,int(_g1*A),1,int(_g1*A))
def right():A=1.825-.0175*_g1;w(1,int(_g1*A),2,int(_g1*A))
def rightArc(r):
	A=abs(_g1)
	if r<_g2:B=0
	else:C=(r-_g2)/(r+_g2)*(1-A*A/200000);B=int(C*A)
	if _g1>0:w(1,A,1,B)
	else:w(2,B,2,A)
def leftArc(r):
	A=abs(_g1)
	if r<_g2:B=0
	else:C=(r-_g2)/(r+_g2)*(1-A*A/200000);B=int(C*A)
	if _g1>0:w(1,B,1,A)
	else:w(2,A,2,B)
def getDistance():pin1.write_digital(1);pin1.write_digital(0);B=machine.time_pulse_us(pin2,1,50000);A=int(B/58.2-.5);return A if A>0 else 255
class Motor:
	def __init__(A,id):A._id=2*id
	def _f2(A,d,s):
		try:i2c.write(16,bytearray([A._id,d,s]))
		except:
			print(_A)
			while True:0
	def rotate(A,s):
		B=abs(s)
		if s>0:A._f2(1,B)
		elif s<0:A._f2(2,B)
		else:A._f2(0,0)
class LEDState:OFF=0;RED=1;GREEN=2;YELLOW=3;BLUE=4;PINK=5;CYAN=6;WHITE=7
def setLED(state,stateR=None):B=state;A=stateR;A=A or B;i2c.write(16,bytearray([11,B,A]))
def setLEDLeft(state):i2c.write(16,bytearray([11,state]))
def setLEDRight(state):i2c.write(16,bytearray([12,state]))
def setAlarm(on):
	if on:music.play(_g3,wait=False,loop=True)
	else:music.stop()
def beep():music.pitch(2000,200,wait=False)
def ir_read_values_as_byte():i2c.write(16,bytearray([29]));A=i2c.read(16,1);return~A[0]
def setServo(S,Angle):
	if S=='S1':A=20
	if S=='S2':A=21
	B=A,Angle;i2c.write(16,bytes(B))
class IR:L3=0;L2=1;L1=2;R1=3;R2=4;R3=5;masks=[1,2,4,8,16,32]
class IRSensor:
	def __init__(A,index):A.index=index
	def read_digital(A):B=ir_read_values_as_byte();return(B&IR.masks[A.index])>>A.index
irLeft=IRSensor(IR.L1)
irRight=IRSensor(IR.R1)
irL1=IRSensor(IR.L1)
irR1=IRSensor(IR.R1)
irL2=IRSensor(IR.L2)
irR2=IRSensor(IR.R2)
irL3=IRSensor(IR.L3)
irR3=IRSensor(IR.R3)
pin2.set_pull(pin2.NO_PULL)
motL=Motor(0)
motR=Motor(1)
delay=sleep
_g3=['c6:1','r','c6,1','r','r','r']