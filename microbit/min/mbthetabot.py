from microbit import*
from utime import ticks_us,sleep_us
from neopixel import*
_g1=50
_g2=40
_g3=40
_g4=bytes(b'\x00\x0b\x0b\x0c\x0c\r\r\r\x0e\x0e\x0f\x0f\x0f\x10\x10\x11\x11\x11\x12\x12\x13\x13\x13\x14\x14\x15\x15\x15\x16\x16\x17\x17\x17\x18\x19\x1a\x1b\x1b\x1c\x1d\x1e\x1f !"##$%&\'()*++,-./0123468:<?ADFILOSVZ^bgkpu{\x81\x87\x8d\x94\x9b\xa3\xab\xb4\xbd\xc6\xd0\xdb\xe6\xf2\xff')
_g5=0
_g6=0
_g7=0
_g8=34
_g9=14
def _f1(dirL,powerL,dirR,powerR):pinsL=pin14,pin13;pinsR=pin16,pin15;pinsL[dirL].write_analog(powerL);pinsL[1-dirL].write_analog(0);pinsR[dirR].write_analog(powerR);pinsR[1-dirR].write_analog(0)
def _f2(side,direction,power):
	if side==0:pins=pin14,pin13
	elif side==2:pins=pin16,pin15
	pins[direction].write_analog(power);pins[1-direction].write_analog(0)
def _f3(r):
	outerSpeed=_g1;rCm=int(r*100);threshold=outerSpeed-max(rCm+20,40)
	if threshold<=0:outerSpeed=min(max(rCm+40,40),100)
	reducedSpeed=0
	if rCm>=4:flattening=(100-outerSpeed)//2;reducedSpeed=(rCm*10-35)/(rCm*(11+(_g7-4)/10)+90+flattening);reducedSpeed=reducedSpeed*outerSpeed
	innerByte=_f4(int(reducedSpeed),0);outerByte=_f4(int(outerSpeed),0);return innerByte,outerByte
def calibrate(offset,differential=0,arcScaling=0):global _g6;global _g5;global _g7;_g5=max(min(int(offset),150),-10);_g6=max(min(int(differential),150),-150);_g7=max(min(arcScaling,50),-15);setSpeed(_g1)
def setSpeed(speed):
	global _g1;global _g2;global _g3;_g1=int(min(max(speed,0),100));powerByte=_f4(_g1,_g5);boost=round((1-_g1/100)*abs(_g6))if _g1>0 else 0;reduction=round(_g1/100*abs(_g6))
	if _g6>0:_g2=powerByte-reduction;_g3=powerByte+boost
	else:_g2=powerByte+boost;_g3=powerByte-reduction
def _f4(speed,offset):speedIndex=int(speed*(len(_g4)-1)/100);return min(_g4[speedIndex]+offset,1023)
def stop():_f1(0,0,0,0)
def forward():_f1(0,_g2,0,_g3)
def backward():_f1(1,_g2,1,_g3)
def left():_f1(1,_g2,0,_g3)
def right():_f1(0,_g2,1,_g3)
def rightArc(radius):inner,outer=_f3(radius);_f1(0,outer,0,inner)
def leftArc(radius):inner,outer=_f3(radius);_f1(0,inner,0,outer)
def getDistance():
	pin12.write_digital(1);sleep_us(10);pin12.write_digital(0);pin12.set_pull(pin15.NO_PULL)
	while pin12.read_digital()==0:0
	start=ticks_us()
	while pin12.read_digital()==1:0
	end=ticks_us();echo=end-start;distance=int(.01715*echo);return distance
def setLED(position,red,green,blue):global _g8;i2c_data=bytearray(5);i2c_data[0]=1;i2c_data[1]=position;i2c_data[2]=red;i2c_data[3]=green;i2c_data[4]=blue;i2c.write(_g8,i2c_data)
def fill(red,green,blue):
	for position in range(_g9):setLED(position,red,green,blue)
def readLine(side):i2c.write(_g8,bytearray([side+1]),False);result=i2c.read(_g8,2);result=result[0]+(result[1]<<8);return result
def readLight(side):i2c.write(_g8,bytearray([side+3]),False);result=i2c.read(_g8,2);result=result[0]+(result[1]<<8);return result