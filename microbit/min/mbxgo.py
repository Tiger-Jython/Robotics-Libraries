from microbit import*
_g1=50
_g2=False
_g3=pin14
_g4=pin13
def checkInit(func):
	def wrapper(*args,**kwargs):
		global _g2
		if not _g2:init_xgo_serial(_g3,_g4)
		return func(*args,**kwargs)
	return wrapper
def _f1(speed,in_min,in_max,out_min,out_max):return(speed-in_min)*(out_max-out_min)//(in_max-in_min)+out_min
@checkInit
def _f2(direction,speed):
	move_buffer=bytearray(9);move_buffer[0]=85;move_buffer[1]=0;move_buffer[2]=9;move_buffer[3]=0;move_buffer[7]=0;move_buffer[8]=170;speed=max(0,min(100,speed))
	if direction==0:move_buffer[4]=48;move_buffer[5]=_f1(speed,0,100,128,255)
	elif direction==1:move_buffer[4]=48;move_buffer[5]=_f1(speed,0,100,128,0)
	elif direction==2:move_buffer[4]=49;move_buffer[5]=_f1(speed,0,100,128,0)
	elif direction==3:move_buffer[4]=49;move_buffer[5]=_f1(speed,0,100,128,255)
	move_buffer[6]=~(9+move_buffer[4]+move_buffer[5])&255;uart.write(move_buffer)
@checkInit
def clampX(milimeters=50):clampBuffer=bytearray(9);clampBuffer[0]=85;clampBuffer[1]=0;clampBuffer[2]=9;clampBuffer[3]=0;clampBuffer[4]=115;clampBuffer[7]=0;clampBuffer[8]=170;clampBuffer[5]=milimeters;clampBuffer[6]=~(124+clampBuffer[5])&255;uart.write(clampBuffer);sleep(1000)
@checkInit
def clampZ(milimeters=50):clampBuffer=bytearray(9);clampBuffer[0]=85;clampBuffer[1]=0;clampBuffer[2]=9;clampBuffer[3]=0;clampBuffer[4]=116;clampBuffer[7]=0;clampBuffer[8]=170;clampBuffer[5]=milimeters;clampBuffer[6]=~(125+clampBuffer[5])&255;uart.write(clampBuffer);sleep(1000)
@checkInit
def clamp(force):clampBuffer=bytearray(9);clampBuffer[0]=85;clampBuffer[1]=0;clampBuffer[2]=9;clampBuffer[3]=0;clampBuffer[4]=113;clampBuffer[7]=0;clampBuffer[8]=170;clampBuffer[5]=force;clampBuffer[6]=~(122+clampBuffer[5])&255;uart.write(clampBuffer);sleep(1000)
def init_xgo_serial(tx_pin,rx_pin,baudrate=115200):global _g2;uart.init(baudrate=baudrate,tx=tx_pin,rx=rx_pin);init_action();_g2=True
def init_action():commands_buffer=bytearray(9);commands_buffer[0]=85;commands_buffer[1]=0;commands_buffer[2]=9;commands_buffer[3]=0;commands_buffer[4]=62;commands_buffer[5]=255;commands_buffer[6]=~326&255;commands_buffer[7]=0;commands_buffer[8]=170;uart.write(commands_buffer);sleep(2000)
@checkInit
def action(id):commands_buffer=bytearray(9);commands_buffer[0]=85;commands_buffer[1]=0;commands_buffer[2]=9;commands_buffer[3]=0;commands_buffer[4]=62;commands_buffer[5]=id;commands_buffer[6]=~(71+id)&255;commands_buffer[7]=0;commands_buffer[8]=170;uart.write(commands_buffer);sleep(2000)
def changeInit(tx,rx):global _g3;global _g4;_g3=tx;_g4=rx;init_xgo_serial(_g3,_g4)
@checkInit
def setSpeed(speed):global _g1;_g1=speed
def forward():_f2(0,_g1)
def backward():_f2(1,_g1)
def left():_f2(2,_g1)
def right():_f2(3,_g1)