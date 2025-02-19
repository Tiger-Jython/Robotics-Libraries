from microbit import*
from neopixel import*
import utime
_g1=[0,9,11,13,15]
_g2=[0,0,0,0,0]
_g3=False
_g4=4
_g5=NeoPixel(pin2,_g4)
_g6=50
_g7=40
_g8=40
_g9=0
_g10=0
_g11=0
_g12=500
_g13=29.1
def _f1(dirL,powerL,dirR,powerR):pinsL=pin1,pin12;pinsR=pin8,pin0;pinsL[dirL].write_analog(powerL);pinsL[1-dirL].write_analog(0);pinsR[dirR].write_analog(powerR);pinsR[1-dirR].write_analog(0)
def _f2(side,direction,power):
	if side==0:pins=pin1,pin12
	elif side==1:pins=pin8,pin0
	pins[direction].write_analog(power);pins[1-direction].write_analog(0)
def _f3(r):
	outerSpeed=_g6;rCm=int(r*100);threshold=outerSpeed-max(rCm+20,40)
	if threshold<=0:outerSpeed=min(max(rCm+40,40),100)
	reducedSpeed=0
	if rCm>=4:flattening=(100-outerSpeed)//2;reducedSpeed=(rCm*10-35)/(rCm*(11+(_g11-4)/10)+90+flattening);reducedSpeed=reducedSpeed*outerSpeed
	innerByte=_f6(int(reducedSpeed),0);outerByte=_f6(int(outerSpeed),0);return innerByte,outerByte
def _f4():global _g3;_g3=True;i2cData=bytearray(2);i2cData[0]=0;i2cData[1]=16;i2c.write(64,i2cData);i2cData[0]=254;i2cData[1]=101;i2c.write(64,i2cData);i2cData[0]=0;i2cData[1]=129;i2c.write(64,i2cData)
def _f5(pin,value,timeout):
	start_time=utime.ticks_us()
	while pin.read_digital()!=value:
		if utime.ticks_diff(utime.ticks_us(),start_time)>timeout:return 0
	start_time=utime.ticks_us()
	while pin.read_digital()==value:
		if utime.ticks_diff(utime.ticks_us(),start_time)>timeout:return 0
	return utime.ticks_diff(utime.ticks_us(),start_time)
def calibrate(offset,differential=0,arcScaling=0):global _g10;global _g9;global _g11;_g9=max(min(int(offset),500),-50);_g10=max(min(int(differential),150),-150);_g11=max(min(arcScaling,50),-15);setSpeed(_g6)
def setSpeed(speed):
	global _g6;global _g7;global _g8;_g6=int(min(max(speed,0),100));powerValue=_f6(_g6,_g9);boost=round((1-_g6/100)*abs(_g10))if _g6>0 else 0;reduction=round(_g6/100*abs(_g10))
	if _g10>0:_g7=powerValue-reduction;_g8=powerValue+boost
	else:_g7=powerValue+boost;_g8=powerValue-reduction
def _f6(speed,offset):analogValue=int(speed*1023/100)+offset;return min(max(analogValue,0),1023)
def stop():_f1(0,0,0,0)
def forward():_f1(0,_g7,0,_g8)
def backward():_f1(1,_g7,1,_g8)
def setServo(servoNum,angle):
	global _g1,_g3
	if _g3==False:_f4()
	offsetNum=servoNum;servoNum=_g1[servoNum];i2cData=bytearray(2);start=0;angle=max(min(angle,90),-90);stop=396+(angle+_g2[offsetNum])*223/90;i2cData[0]=6+servoNum*4+2;i2cData[1]=int(stop)+255;i2c.write(64,i2cData);i2cData[0]=6+servoNum*4+3;i2cData[1]=int(stop)>>8;i2c.write(64,i2cData)
def clearServos():setServo(0,0);setServo(1,0);setServo(2,0);setServo(3,0);setServo(4,0);sleep(500)
def steer(angle):angle=max(min(angle,45),-45);setServo(1,angle);setServo(2,-angle);setServo(3,-angle);setServo(4,angle);sleep(500)
def setLED(pos,red,green,blue):_g5[pos]=red,green,blue;_g5.show()
def fill(red,green,blue):
	for i in range(_g4):_g5[i]=red,green,blue
	_g5.show()
def getDistance():
	trig=pin13;echo=pin13;d=10;trig.set_pull(trig.NO_PULL)
	for _ in range(10):
		trig.write_digital(0);utime.sleep_us(2);trig.write_digital(1);utime.sleep_us(10);trig.write_digital(0);duration=_f5(echo,1,_g12*_g13)
		if duration>0:d=duration;break
	return round(d/_g13)
def calibrateServo(pos,angleDifferential):global _g2;angleDifferential=max(min(angleDifferential,90),-90);_g2[pos]=angleDifferential;clearServos()