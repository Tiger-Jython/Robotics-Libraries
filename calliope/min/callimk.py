import gc
from calliope_mini import i2c,sleep
i2c.init()
_g1=30
_g2=.09
def w(d1,d2,s1,s2):i2c.write(16,bytearray([0,d1,s1]));i2c.write(16,bytearray([2,d2,s2]))
def forward():w(0,0,_g1,_g1)
def backward():w(1,1,_g1,_g1)
def stop():w(0,0,0,0)
def right():w(0 if _g1>0 else 1,1 if _g1>0 else 0,_g1,_g1)
def left():w(1 if _g1>0 else 0,0 if _g1>0 else 1,_g1,_g1)
def rightArc(r):
	A=abs(_g1)
	if r<_g2:B=0
	else:C=(r-_g2)/(r+_g2)*(1-A*A/200000);B=int(C*A)
	if _g1>0:w(0,0,A,B)
	else:w(1,1,B,A)
def leftArc(r):
	A=abs(_g1)
	if r<_g2:B=0
	else:C=(r-_g2)/(r+_g2)*(1-A*A/200000);B=int(C*A)
	if _g1>0:w(0,0,B,A)
	else:w(1,1,A,B)
def setSpeed(speed):
	A=speed;global _g1
	if A<15:_g1=15
	else:_g1=A
def motorL(dir,speed):i2c.write(16,bytearray([0,dir,speed]))
def motorR(dir,speed):i2c.write(16,bytearray([2,dir,speed]))
def led(right_left,on_off):
	A=bytearray(2)
	if right_left==0:A[0]=11
	else:A[0]=12
	A[1]=on_off;i2c.write(16,A)
def setLEDLeft(on):led(1,on)
def setLEDRight(on):led(0,on)
def setLED(on):led(1,on);led(0,on)
def rgbLED(red,green,blue):A=bytearray(2);A[0]=24;A[1]=red;B=bytearray(2);B[0]=25;B[1]=green;C=bytearray(2);C[0]=26;C[1]=blue;i2c.write(16,A);i2c.write(16,B);i2c.write(16,C)
def getDistance():i2c.write(16,bytearray([40]));sleep(20);A=i2c.read(16,2);B=A[0]<<8|A[1];return B
def irLeftValue():i2c.write(16,bytearray([29]));A=i2c.read(16,1)[0];return 0 if A&1!=0 else 1
def irRightValue():i2c.write(16,bytearray([29]));A=i2c.read(16,1)[0];return 0 if A&2!=0 else 1
def setServo(S,Angle):
	if S=='S1':A=20
	if S=='S2':A=21
	i2c.write(16,bytearray([A,Angle]))
exit=stop
delay=sleep