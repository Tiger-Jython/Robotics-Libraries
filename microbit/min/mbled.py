from neopixel import*
import gc
from microbit import pin2
_g1=24
_g2=NeoPixel(pin2,_g1)
def fill(red,green,blue):
	for i in range(_g1):_g2[i]=red,green,blue
	_g2.show()
def set_led(pos,red,green,blue):_g2[pos]=red,green,blue;_g2.show()
def clear():_g2.clear()
def shift_by(amount):
	shifted_copy=[None]*_g1
	for n in range(0,_g1):next_i=(n+amount)%_g1;shifted_copy[n]=_g2[next_i]
	for n in range(0,_g1):_g2[n]=shifted_copy[n]
	_g2.show()
def lerp_RGB(r1,g1,b1,r2,g2,b2,percent):
	if percent<.0 or percent>1e2:raise RuntimeError("Argument 'percent' must be between 0 and 100.")
	red=max(0,min(255,round(r1+(r2-r1)*(percent/1e2))));green=max(0,min(255,round(g1+(g2-g1)*(percent/1e2))));blue=max(0,min(255,round(b1+(b2-b1)*(percent/1e2))));return red,green,blue