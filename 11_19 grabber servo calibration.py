
from machine import Pin, PWM, ADC
from time import sleep

servo = PWM(Pin(15))
servo.freq(50)

feedback = ADC(Pin(26))

MIN_PULSE = 500
MAX_PULSE = 2500

def set_pulse(pulse):
    duty = int((pulse / 20000) * 65535)
    servo.duty_u16(duty)

def read_adc():
    total = 0

    for i in range(50):
        total += feedback.read_u16()
        sleep(0.01)

    return total / 50

while True:

    print("\nServo calibration")
    print("1. Minimum position")
    print("2. Middle position")
    print("3. Maximum position")

    choice = input("Select position (1, 2 or 3): ")

    if choice == "1":
        set_pulse(MIN_PULSE)

    elif choice == "2":
        set_pulse((MIN_PULSE + MAX_PULSE) // 2)

    elif choice == "3":
        set_pulse(MAX_PULSE)

    else:
        continue

    sleep(2)

    adc_value = read_adc()

    print("ADC reading:", adc_value)
