from microbit import button_a,button_b,pin0,pin1,pin2,pin_logo,sleep
POLLING_DELAY=100
def wait_for_press(button='any'):
	A=button;button_a.was_pressed();button_b.was_pressed()
	if A=='a'or A=='A':
		while not button_a.was_pressed():sleep(POLLING_DELAY)
	elif A=='b'or A=='B':
		while not button_b.was_pressed():sleep(POLLING_DELAY)
	elif A=='any'or A=='ANY':
		while not button_a.was_pressed()and not button_b.was_pressed():sleep(POLLING_DELAY)
	elif A=='both'or A=='ab'or A=='AB':
		while not(button_a.is_pressed()and button_b.is_pressed()):sleep(POLLING_DELAY)
		while button_a.is_pressed()or button_b.is_pressed():sleep(POLLING_DELAY)
	else:raise RuntimeError("Button to wait for must be either: 'a', 'b', 'any' or 'both'.")
def wait_for_touch(pin='logo'):
	B=pin;A=pin_logo
	if B=='pin0':A=pin0
	elif B=='pin1':A=pin1
	elif B=='pin2':A=pin2
	elif B=='logo'or B=='pin_logo'or B=='pinLogo':A=pin_logo
	else:raise RuntimeError("Argument 'pin' must be one of: 'pin_logo', 'pin0', 'pin1' or 'pin2'.")
	A.set_touch_mode(A.CAPACITIVE)
	while not A.is_touched():sleep(POLLING_DELAY)