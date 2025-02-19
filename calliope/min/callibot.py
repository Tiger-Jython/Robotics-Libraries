_B=True
_A='Please switch on Robot!'
import gc
from calliope_mini import i2c,sleep
_g1=.06
def w(d1,d2,s1,s2):
	try:i2c.write(32,bytearray([0,d1,s1]));i2c.write(32,bytearray([2,d2,s2]))
	except:
		print(_A)
		while _B:0
def setSpeed(speed):global _g2;_g2=speed+40
def forward():w(0,0,_g2,_g2)
def backward():w(1,1,_g2,_g2)
def stop():w(0,0,0,0)
def right():A=int(_g2*1.1);w(0 if _g2>0 else 1,1 if _g2>0 else 0,A,A)
def left():A=int(_g2*1.1);w(1 if _g2>0 else 0,0 if _g2>0 else 1,A,A)
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
def setLEDLeft(on):
	try:i2c.write(33,bytearray([0,0]))
	except:
		print(_A)
		while _B:0
	if on==1:i2c.write(33,bytearray([0,1]))
	else:i2c.write(33,bytearray([0,0]))
def setLEDRight(on):
	try:i2c.write(33,bytearray([0,0]))
	except:
		print(_A)
		while _B:0
	if on==1:i2c.write(33,bytearray([0,2]))
	else:i2c.write(33,bytearray([0,0]))
def setLED(on):
	try:i2c.write(33,bytearray([0,0]))
	except:
		print(_A)
		while _B:0
	if on==1:i2c.write(33,bytearray([0,3]))
	else:i2c.write(33,bytearray([0,0]))
def irLeftValue():
	try:
		A=i2c.read(33,1)
		if A[0]==130 or A[0]==131:return 1
		else:return 0
	except:
		print(_A)
		while _B:0
def irRightValue():
	try:
		A=i2c.read(33,1)
		if A[0]==129 or A[0]==131:return 1
		else:return 0
	except:
		print(_A)
		while _B:0
def getDistance():
	try:A=i2c.read(33,3);B=(256*A[1]+A[2])/10;return B
	except:
		print(_A)
		while _B:0
def tsValue():
	try:
		A=i2c.read(33,1)
		if A[0]==140 or A[0]==143:return 1
		else:return 0
	except:
		print(_A)
		while _B:0
def tsLeftValue():
	try:
		A=i2c.read(33,1)
		if A[0]==136 or A[0]==139:return 1
		else:return 0
	except:
		print(_A)
		while _B:0
def tsRightValue():
	try:
		A=i2c.read(33,1)
		if A[0]==132 or A[0]==135:return 1
		else:return 0
	except:
		print(_A)
		while _B:0
exit=stop
delay=sleep
_g2=90