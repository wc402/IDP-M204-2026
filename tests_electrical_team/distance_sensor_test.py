# arya_tof_test.py
# Prints the ToF distance about 4 times a second. Stop with Thonny's Stop.
#
# Wiring: red -> 3V3, black -> GND,
#         SDA (green) -> GP8 (pin 11), SCL (blue) -> GP9 (pin 12)
# Works with the VL53L0X or the TMF8701 - it checks which one is plugged in.
# Needs the course "libs" folder on the Pico.

from machine import Pin, I2C
from utime import sleep_ms

SDA_PIN = 8
SCL_PIN = 9

i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)
found = i2c.scan()
print("I2C devices found:", [hex(a) for a in found])

if 0x29 in found:
    from libs.VL53L0X.VL53L0X import VL53L0X
    tof = VL53L0X(i2c)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
    tof.start()
    print("Sensor: VL53L0X")

    def read_mm():
        d = tof.read()
        return d if d < 8000 else 0      # about 8190 means nothing in range

elif 0x41 in found:
    from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8701
    tof = DFRobot_TMF8701(i2c_bus=i2c)
    print("Sensor: TMF8701 - starting, takes a few seconds...")
    while tof.begin() != 0:
        print("  start failed, trying again")
        sleep_ms(500)
    tof.start_measurement(calib_m=tof.eMODE_NO_CALIB, mode=tof.eCOMBINE)   # 0 to 60 cm

    def read_mm():
        # Reads the sensor's own mm value. The library's get_distance_mm()
        # rescales it using a whole-second clock, which can give 0 or a
        # value that is too big when read this often.
        tof.is_data_ready()
        r = tof.result_dict
        return (r["disH"] << 8) | r["disL"]

else:
    raise RuntimeError("No ToF sensor found on GP8/GP9 - check the four wires")

while True:
    d = read_mm()
    if d == 0:
        print("nothing in range")
    else:
        print(d, "mm")
    sleep_ms(250)