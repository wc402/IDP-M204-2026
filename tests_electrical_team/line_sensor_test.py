from machine import Pin
from utime import sleep

def test_line_sensors_poll():
    "Simple poll of all four line sensors"
    # Red → 3V3 (header pin 36), Black → GND (pin 38), Green → the pin below
    # 1 over white, 0 over black
    far_left  = Pin(18, Pin.IN, Pin.PULL_DOWN)   # GP18 = header pin 24
    left      = Pin(19, Pin.IN, Pin.PULL_DOWN)   # GP19 = header pin 25
    right     = Pin(20, Pin.IN, Pin.PULL_DOWN)   # GP20 = header pin 26
    far_right = Pin(22, Pin.IN, Pin.PULL_DOWN)   # GP22 = header pin 29
    
    while True:
        # Poll the values
        print(f"FL = {far_left.value()}  L = {left.value()}  R = {right.value()}  FR = {far_right.value()}")
        sleep(0.2)


if __name__ == "__main__":
    test_line_sensors_poll()