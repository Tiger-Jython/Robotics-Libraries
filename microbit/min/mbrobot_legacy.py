import gc
from microbit import i2c,pin1,pin2,pin8,pin12,pin13,pin14,sleep
import machine
_g1=.097
def w(d1,d2,s1,s2):
	try:i2c.write(16,bytearray([0,d1,s1]));i2c.write(16,bytearray([2,d2,s2]))
	except:
		print('Please switch on mbRobot!')
		while True:0
def setSpeed(speed):
	A=speed;global _g2
	if A<20:_g2=A+5
	else:_g2=A
def forward():w(0,0,_g2,_g2)
def backward():w(1,1,_g2,_g2)
def stop():w(0,0,0,0)
def right():w(0 if _g2>0 else 1,1 if _g2>0 else 0,int(_g2*.9),int(_g2*.9))
def left():w(1 if _g2>0 else 0,0 if _g2>0 else 1,int(_g2*.9),int(_g2*.9))
def rightArc(r):
	A=abs(_g2)
	if r<_g1:B=0
	else:C=(r-_g1)/(r+_g1)*(1-A*A/200000);B=int(C*A)
	if _g2>0:w(0,0,A,B)
	else:w(1,1,B,A)
def leftArc(r):
	A=abs(_g2)
	if r<_g1:B=0
	else:C=(r-_g1)/(r+_g1)*(1-A*A/200000);B=int(C*A)
	if _g2>0:w(0,0,B,A)
	else:w(1,1,A,B)
exit=stop
delay=sleep
def getDistance():pin1.write_digital(1);pin1.write_digital(0);B=machine.time_pulse_us(pin2,1,50000);A=int(B/58.2+.5);return A if A>0 else 255
def setLED(on):pin8.write_digital(on);pin12.write_digital(on)
def setServo(S,Angle):
	if S=='S1':A=20
	if S=='S2':A=21
	B=A,Angle;i2c.write(16,bytes(B))
pin2.set_pull(pin2.NO_PULL)
_g2=50
irLeft=pin13
irRight=pin14
ledLeft=pin8
ledRight=pin12
forward()