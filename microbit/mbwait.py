from microbit import button_a, button_b, pin0, pin1, pin2, pin_logo, sleep

# choose the reactivity of the press/touch sensing in ms. Default 100ms is 10 checks per second.
POLLING_DELAY = 100

# Let the microbit wait until a certain button of choice was pressed (and released).


def wait_for_press(button='any'):
    button_a.was_pressed()
    button_b.was_pressed()
    # busy wait until a chosen button was pressed.
    if button == 'a' or button == 'A':
        while not button_a.was_pressed():
            sleep(POLLING_DELAY)
    elif button == 'b' or button == 'B':
        while not button_b.was_pressed():
            sleep(POLLING_DELAY)
    elif button == 'any' or button == 'ANY':
        while (not button_a.was_pressed()) and (not button_b.was_pressed()):
            sleep(POLLING_DELAY)
    elif button == 'both' or button == 'ab' or button == 'AB':
        while not (button_a.is_pressed() and button_b.is_pressed()):
            sleep(POLLING_DELAY)
        while button_a.is_pressed() or button_b.is_pressed():
            sleep(POLLING_DELAY)
    else:
        raise RuntimeError(
            "Button to wait for must be either: 'a', 'b', 'any' or 'both'.")

# Let the microbit wait until a certain touch-sensitive pin of choice is touched.


def wait_for_touch(pin='logo'):
    # busy wait until a given pin/logo is pressed.
    p = pin_logo
    if pin == 'pin0':
        p = pin0
    elif pin == 'pin1':
        p = pin1
    elif pin == 'pin2':
        p = pin2
    elif pin == 'logo' or pin == 'pin_logo' or pin == 'pinLogo':
        p = pin_logo
    else:
        raise RuntimeError(
            "Argument 'pin' must be one of: 'pin_logo', 'pin0', 'pin1' or 'pin2'.")
    p.set_touch_mode(p.CAPACITIVE)
    while not p.is_touched():
        sleep(POLLING_DELAY)
