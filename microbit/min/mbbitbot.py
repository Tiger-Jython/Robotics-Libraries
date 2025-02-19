from microbit import*
from neopixel import*
from utime import ticks_us,sleep_us
_g1=200
_g2=12
_g3=NeoPixel(pin13,_g2)
_g4=0
_g5=0
def w(leftforward,leftbackward,rightforward,rightbackward):
	if leftforward>0 or rightforward>0:pin16.write_analog(leftforward+_g4);pin8.write_analog(leftbackward);pin14.write_analog(rightforward-_g4);pin12.write_analog(rightbackward)
	elif leftbackward>0 or rightbackward>0:pin16.write_analog(leftforward);pin8.write_analog(leftbackward+_g4);pin14.write_analog(rightforward);pin12.write_analog(rightbackward-_g4)
	elif leftforward==0 and rightforward==0 and leftbackward==0 and rightbackward==0:pin16.write_analog(0);pin8.write_analog(0);pin14.write_analog(0);pin12.write_analog(0)
def forward():w(_g1,0,_g1,0)
def backward():w(0,_g1,0,_g1)
def stop():w(0,0,0,0)
def right():w(0,_g1,_g1,0)
def left():w(_g1,0,0,_g1)
def set_led(pos,red,green,blue):_g3[pos]=red,green,blue;_g3.show()
def fill(red,green,blue):
	for i in range(_g2):_g3[i]=red,green,blue
	_g3.show()
def getDistance():
	pin15.write_digital(1);sleep_us(10);pin15.write_digital(0);pin15.set_pull(pin15.NO_PULL)
	while pin15.read_digital()==0:0
	start=ticks_us()
	while pin15.read_digital()==1:0
	end=ticks_us();echo=end-start;distance=int(.01715*echo);return distance
def calibrate(offset,differential=0):global _g4;global _g5;global _g8;_g5=max(min(int(offset),50),-50);_g4=max(min(int(differential),50),-50);_g8=max(min(arcScaling,50),-50);setSpeed(_g1/1023*100)
def setSpeed(percent):global _g1;speed=percent/100*1023;speed+=_g5/100*1023;speed=min(max(speed,0),1023);_g1=speed
def getLine(bit):
	mask=1<<bit;value=0
	try:value=i2c.read(28,1)[0]
	except OSError:pass
	if value&mask>0:return 1
	else:return 0
def getLight(index):
	if index==0:return pin1.read_analog()
	elif index==1:return pin2.read_analog()
def leftArc(radius):speed=_g1;inner_wheel_speed=speed*(radius/(radius+1));w(inner_wheel_speed,0,speed,0)
def rightArc(radius):speed=_g1;inner_wheel_speed=speed*(radius/(radius+1));w(speed,0,inner_wheel_speed,0)