from machine import Pin
from utime import sleep

def test_input_poll():
    "Simple poll of input"
    input_pin = 18  # Pin 18 = GP18 (labelled 24 on the jumper)
    input = Pin(input_pin, Pin.IN, Pin.PULL_DOWN) # Think carefully whether you need pull up or pull down

    while True:
        # Poll the value
        value = input.value()
        print(f"Input = {value}")
        sleep(0.2)


def input_irq(p):	
    "Interrupt handler"
    # print(p)
    value = p.value()
    print(f"Input changed, value={value}")


def test_input_irq():
    "More advanced, interrupt based input handling"
    left  = Pin(18, Pin.IN, Pin.PULL_DOWN)   # header pin 24
    right = Pin(19, Pin.IN, Pin.PULL_DOWN)   # header pin 25
    while True:
        print(f"L={left.value()}  R={right.value()}")
        sleep(0.2)


if __name__ == "__main__":
    test_input_poll()
    # test_input_irq()