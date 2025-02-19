from microbit import*
from neopixel import*
import utime
_g1=4
_g2=NeoPixel(pin13,_g1)
_g3=50
_g4=90
_g5=90
_g6=0
_g7=0
_g8=0
_g9=500
_g10=29.1
def _f1(dirL,powerL,dirR,powerR):pin8.write_analog(powerL if dirL==1 else 0);pin12.write_analog(0 if dirL==1 else powerL);pin16.write_analog(0 if dirR==1 else powerR);pin14.write_analog(powerR if dirR==1 else 0)
def _f2(pin,value,timeout):
	start_time=utime.ticks_us()
	while pin.read_digital()!=value:
		if utime.ticks_diff(utime.ticks_us(),start_time)>timeout:return 0
	start_time=utime.ticks_us()
	while pin.read_digital()==value:
		if utime.ticks_diff(utime.ticks_us(),start_time)>timeout:return 0
	return utime.ticks_diff(utime.ticks_us(),start_time)
def _f3(r):
	outerSpeed=_g3
	if r>0:innerSpeed=outerSpeed*max(.2,min(1,1-r/100))
	else:innerSpeed=0
	innerByte=_f4(int(innerSpeed),0);outerByte=_f4(int(outerSpeed),0);return innerByte,outerByte
def _f4(speed,offset):analogValue=int(speed*255/100)+offset;return min(max(analogValue,0),255)
def calibrate(offset,differential=0,arcScaling=0):global _g7;global _g6;global _g8;_g6=max(min(int(offset),100),-10);_g7=max(min(int(differential),150),-150);_g8=max(min(arcScaling,50),-15);setSpeed(_g3)
def setSpeed(speed):
	global _g3;global _g4;global _g5;_g3=int(min(max(speed,0),100));powerByte=_f4(_g3,_g6);boost=round((1-_g3/100)*abs(_g7))if _g3>0 else 0;reduction=round(_g3/100*abs(_g7))
	if _g7>0:_g4=powerByte-reduction;_g5=powerByte+boost
	else:_g4=powerByte+boost;_g5=powerByte-reduction
def stop():_f1(0,0,0,0)
def forward():_f1(0,_g4,0,_g5)
def backward():_f1(1,_g4,1,_g5)
def left():_f1(1,_g4,0,_g5)
def right():_f1(0,_g4,1,_g5)
def rightArc(radius):inner,outer=_f3(radius);_f1(0,outer,0,inner)
def leftArc(radius):inner,outer=_f3(radius);_f1(0,inner,0,outer)
def setLED(pos,red,green,blue):_g2[pos]=red,green,blue;_g2.show()
def fill(red,green,blue):
	for i in range(_g1):_g2[i]=red,green,blue
	_g2.show()
def getDistance():
	trig=pin15;echo=pin15;d=10;trig.set_pull(trig.NO_PULL)
	for _ in range(10):
		trig.write_digital(0);utime.sleep_us(2);trig.write_digital(1);utime.sleep_us(10);trig.write_digital(0);duration=_f2(echo,1,_g9*_g10)
		if duration>0:d=duration;break
	return round(d/_g10)