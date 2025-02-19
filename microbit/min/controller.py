_B=False
_A=1.
from microbit import run_every,pin13,pin14,pin15,pin16,pin8,pin1,pin2,pin12,button_a,button_b,sleep
class _Controller_Button:
	def __init__(A,pin):B=pin;A._pin=B;A.previous_state=0;A._press_count=0;A._pressed_before=_B;B.set_pull(B.PULL_UP)
	def _f3(A):
		B=1-A._pin.read_digital()
		if B==1 and A.previous_state==0:A._press_count+=1;A._pressed_before=True
		A.previous_state=B
	def is_pressed(A):return _B if A._pin.read_digital()else True
	def was_pressed(A):B=A._pressed_before;A._pressed_before=_B;return B
	def get_presses(A):B=A._press_count;A._press_count=0;return B
class _Controller_Analog_Stick:
	def __init__(A,pinX,pinY,pinZ):A.pin_x=pinX;A.pin_y=pinY;A.button_z=_Controller_Button(pinZ);A.dead_zone=.01;A.center_x=0;A.center_y=0;A.min_x=-1;A.max_x=1;A.min_y=-1;A.max_y=1
	def calibrate(A,dead_zone,center_x=.0,center_y=.0,x_min=-_A,x_max=_A,y_min=-_A,y_max=_A):A.dead_zone=min(.2,max(.01,dead_zone));A.center_x=min(.4,max(-.4,center_x));A.center_y=min(.5,max(-.5,center_y));A.min_x=min(-.5,max(-_A,x_min));A.max_x=min(_A,max(.5,x_max));A.min_y=min(-.5,max(-_A,y_min));A.max_y=min(_A,max(.5,y_max))
	def _f5(C,value,center,v_min,v_max):
		B=center;A=value-_A-B
		if abs(A)-C.dead_zone/2.>.0:
			if A<.0:A=A/abs(v_min-B)
			else:A=A/abs(v_max-B)
		A=min(_A,max(-_A,A));A=.0 if abs(A)<=C.dead_zone else A;return A
	def get_x(A):B=A.pin_x.read_analog()/512.;C=A._f5(B,A.center_x,A.min_x,A.max_x);return C
	def get_y(A):B=A.pin_y.read_analog()/512.;C=A._f5(B,A.center_y,A.min_y,A.max_y);return C
	def get_z(A):return 1 if A.button_z.is_pressed()else 0
	def is_pressed(A):return A.button_z.is_pressed()
	def was_pressed(A):return A.button_z.was_pressed()
	def get_presses(A):return A.button_z.get_presses()
def vibrate(state):pin12.write_digital(state)
joystick=_Controller_Analog_Stick(pin1,pin2,pin8)
button_z=joystick.button_z
button_c=_Controller_Button(pin13)
button_green=button_c
button_d=_Controller_Button(pin14)
button_yellow=button_d
button_e=_Controller_Button(pin15)
button_red=button_e
button_f=_Controller_Button(pin16)
button_blue=button_f
trigger_left=button_a
trigger_right=button_b
def _f1():global button_c;global button_d;global button_e;global button_f;global joystick;button_c._f3();button_d._f3();button_e._f3();button_f._f3();joystick.button_z._f3()
run_every(_f1,days=0,h=0,min=0,s=0,ms=33)