import gc
from microbit import i2c,pin1,pin2,pin8,pin12,pin13,pin14,sleep
import machine
class Motor:
	def __init__(A,id):A._id=2*id
	def rotate(A,s):
		B=abs(s)
		if s>0:A._f2(0,B)
		elif s<0:A._f2(1,B)
		else:A._f2(0,0)
	def _f2(A,d,s):
		try:i2c.write(16,bytearray([A._id,d,s]))
		except:
			print('Please switch on mbRobot!')
			while True:0
delay=sleep
def getDistance():pin1.write_digital(1);pin1.write_digital(0);B=machine.time_pulse_us(pin2,1,50000);A=int(B/58.2+.5);return A if A>0 else 255
def setLED(on):pin8.write_digital(on);pin12.write_digital(on)
pin2.set_pull(pin2.NO_PULL)
irLeft=pin13
irRight=pin14
ledLeft=pin8
ledRight=pin12
motL=Motor(0)
motR=Motor(1)