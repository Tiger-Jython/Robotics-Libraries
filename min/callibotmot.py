import gc
from calliope_mini import i2c,sleep
import machine
class Motor:
	def __init__(A,id):A._id=id
	def _f2(B,d,s):
		if B._id==0:A=0
		else:A=2
		try:i2c.write(32,bytearray([A,d,s]))
		except:
			print('Please switch on mbRobot!')
			while True:0
	def rotate(B,s):
		A=abs(s);A=A+50
		if s>0:B._f2(0,A)
		elif s<0:B._f2(1,A)
		else:B._f2(0,0)
delay=sleep
def setLED(on):
	if on==1:i2c.write(33,bytearray([0,3]))
	else:i2c.write(33,bytearray([0,0]))
motL=Motor(0)
motR=Motor(2)