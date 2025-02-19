from microbit import*
_g1=0
_g2=0
_g3=0
_g4=50
_g5=True
_g6=False
def makeGlow():global _g6;display.set_pixel(2,2,9);_g6=True
def clear():display.clear()
def forward():_f1(1)
def back():_f1(-1)
def right(angle):global _g3;_g3=(_g3+angle)%360
def left(angle):right(-angle)
def setPos(x,y):global _g1,_g2;_g1=x;_g2=y;_f2()
def getPos():return _g1,_g2
def setSpeed(speed):global _g4;_g4=speed
def showTrace(enable):global _g5;_g5=enable
def isLit():return display.get_pixel(_g1+2,4-(_g2+2))==9
def _f1(s):
	global _g1,_g2;sleep(2000-_g4*20);d=_g3//45
	if d in[1,2,3]:_g1+=s
	if d in[5,6,7]:_g1-=s
	if d in[0,1,7]:_g2+=s
	if d in[3,4,5]:_g2-=s
	_f2()
def _f2():
	if not _g6:print('Use "makeGlow()" to create a Glow.');raise Exception('Glow not initialized.')
	if not _g5:display.clear()
	if-2<=_g1<=2 and-2<=_g2<=2:display.set_pixel(_g1+2,4-(_g2+2),9)