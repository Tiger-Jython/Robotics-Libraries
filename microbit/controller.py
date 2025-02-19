# Controller v1.0, Date 21.06.24
# Enables easy use of the DFRobot Micro:bit GamePad by simulating buttons the same way as the microbit internal ones.
from microbit import run_every, pin13, pin14, pin15, pin16, pin8, pin1, pin2, pin12, button_a, button_b, sleep

class _Controller_Button:
    #""" Simulated Button for regular pins with same functionality as the micro:bit buttons a and b."""
    
    def __init__(self, pin):
        # """create a new simulated button from a digital pin

        #     Parameter:
        #     pin (MicroBitDigitalPin): pin to use as button
        # """
        self._pin = pin
        self.previous_state = 0
        self._press_count = 0
        self._pressed_before = False
        pin.set_pull(pin.PULL_UP)
    
    def _update_state(self):
        # """ internally update the buttons state."""
        current_state = 1 - self._pin.read_digital()
        
        if current_state == 1 and self.previous_state == 0: # Low -> High
            self._press_count += 1
            self._pressed_before = True
        
        self.previous_state = current_state

    def is_pressed(self):
        # """ check if the button is currently pressed.

        #     Returns:
        #         bool: if button is currently pressed.
        # """
        return False if self._pin.read_digital() else True
    
    def was_pressed(self):
        # """ check if button was pressed down before. Resets upon call. 

        #     Returns:
        #         bool: True if button was pressed down after last call of this function.
        # """
        state = self._pressed_before
        self._pressed_before = False
        return state
    
    def get_presses(self):
        # """ get the amount of button presses since last call.
        
        #     Returns:
        #         int: number of button (down) presses since last call of this function.
        # """
        count = self._press_count
        self._press_count = 0
        return count

class _Controller_Analog_Stick:
    # """ class that encapsulates the right analog stick of the controller. 
    #    This includes the turning in an xy-plane and the pressing (z-button)."""

    def __init__(self, pinX, pinY, pinZ):
        # """ creates a new analog-stick given its input pins.
        
        #     Parameters:
        #         pinX (MicroBitAnalogDigitalPin): The pin to use for the x-axis (left-right).
        #         pinY (MicroBitAnalogDigitalPin): The pin to use for the y-axis (up-down).
        #         pinZ (MicroBitDigitalPin): The pin to use for the z-button.
        # """
        self.pin_x = pinX
        self.pin_y = pinY
        self.button_z = _Controller_Button(pinZ)
        self.dead_zone = 0.01
        self.center_x = 0
        self.center_y = 0
        self.min_x = -1
        self.max_x = 1
        self.min_y = -1
        self.max_y = 1
    
    def calibrate(self, dead_zone, 
                  center_x=0.0, center_y=0.0, 
                  x_min=-1.0, x_max=1.0, 
                  y_min=-1.0, y_max=1.0):
        # """ calibrate the analog-stick to remove drift (nonzero values even in resting position) 
        # and rescale to full [-1,1] range for the xy-inputs.
        
        # After calibration, the analog-stick 
        #       - does not react (returns 0) until it exceeds a value above the "dead_zone" range.
        #       - returns values in the range [-1, 1] when pushed to the extremes and 0 at rest.
        
        # Parameters:
        #     dead_zone (int): range of xy-values (negative too) that should be mapped to 0. 
        #                      Default: 0.01 
        #     center_x (int):  returned value for get_x, when the stick is not moved (before calibration). 
        #                      Default: 0.0
        #     center_y (int):  returned value for get_y, when the stick is not moved (before calibration). 
        #                      Default: 0.0
        #     x_min (int):     minimal possible value for x (before calibration). Default: -1.0
        #     x_max (int):     maximal possible value for x (before calibration). Default:  1.0
        #     y_min (int):     minimal possible value for y (before calibration). Default: -1.0
        #     y_max (int):     maximal possible value for y (before calibration). Default:  1.0
        # """
        self.dead_zone = min(0.2, max(0.01,dead_zone))
        self.center_x = min(0.4, max(-0.4,center_x))
        self.center_y = min(0.5, max(-0.5,center_y))
        self.min_x = min(-0.5, max(-1.0,x_min))
        self.max_x = min(1.0, max(0.5,x_max))
        self.min_y = min(-0.5, max(-1.0,y_min))
        self.max_y = min(1.0, max(0.5,y_max))

    def _remap(self, value, center, v_min, v_max):
        # """ internal function that applies remapping of the values according to the calibration.
        # The returned value will live in a possible space from [-1,1] with center at 0.
        
        # Parameters:
        #     value (float): the input value to remap to the desired range.
        #     center (float): the resting value before calibration.
        #     v_min (float): the minimally attainable value before calibration.
        #     v_max (float): the maximally attainable value before calibration.

        # Returns:
        #     v (float): remapped parameter value according to calibration.
        # """
        v = value - 1.0 - center
        if abs(v) - self.dead_zone/2.0 > 0.0:
            if v < 0.0:
                v = v / abs(v_min - center)
            else:
                v = v / abs(v_max - center)
        v = min(1.0, max(-1.0, v))
        v = 0.0 if abs(v) <= self.dead_zone else v
        return v

    def get_x(self):
        # """ get the current x-axis value of the analog stick.
        
        # Returns:
        #     (float): position of x-axis in range [-1,1] (left to right). 0 is resting position. (after calibration)
        # """
        v_raw = (self.pin_x.read_analog() / 512.0)
        v = self._remap(v_raw, self.center_x, self.min_x, self.max_x)
        return v

    def get_y(self):
        # """ get the current y-axis value of the analog stick.
        
        # Returns:
        #     (float): position of y-axis in range [-1,1] (down to up). 0 is resting position. (after calibration)
        # """
        v_raw = (self.pin_y.read_analog() / 512.0)
        v = self._remap(v_raw, self.center_y, self.min_y, self.max_y)
        return v

    def get_z(self):
        # """ get the current z-button state as an int. 1 = pressed, 0 = not pressed. """
        return 1 if self.button_z.is_pressed() else 0

    def is_pressed(self):
        # """ returns if the z-button is currently pressed as a bool."""
        return self.button_z.is_pressed()
    
    def was_pressed(self):
        # """ returns if the z-button was pressed (down) before the last call to this function."""
        return self.button_z.was_pressed()
    
    def get_presses(self):
        # """ returns how often the z-button was pressed (down) before the last call to this function."""
        return self.button_z.get_presses()

# Controller LED and vibration motor
def vibrate(state):
    # """ Set the state of the controllers vibration motor. 0=Off, 1=On.
    # Also affects the controllers blue LED next to the motor. """
    pin12.write_digital(state)

# Left side of controller (black joystick)
joystick = _Controller_Analog_Stick(pin1, pin2, pin8)
# also make the joystick button accessible independently.
button_z = joystick.button_z

# Right side of controller (4 colored buttons)
button_c = _Controller_Button(pin13)
button_green = button_c
button_d = _Controller_Button(pin14)
button_yellow = button_d
button_e = _Controller_Button(pin15)
button_red = button_e
button_f = _Controller_Button(pin16)
button_blue = button_f

# Back side of controller (2 white buttons, same as default buttons)
trigger_left = button_a
trigger_right = button_b


def _update_controller_buttons():
    # """ function to be called repeatedly that updates the state of all the controllers buttons. 
    # It is necessary to run this function regularly to simulate the standard microbit button behaviour. """
    global button_c
    global button_d
    global button_e
    global button_f
    global joystick

    button_c._update_state()
    button_d._update_state()
    button_e._update_state()
    button_f._update_state()
    joystick.button_z._update_state()

run_every(_update_controller_buttons, days=0, h=0, min=0, s=0, ms=33) # ~30 Updates per Second
