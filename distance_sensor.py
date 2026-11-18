from machine import Pin, PWM, I2C
from libs.VL53L0X.VL53L0X import VL53L0X

class ToF:
    def __init__(self, sda=8, scl=9):
        i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=100000)
        if ox29 not in ic2.scan():
            raise RuntimeError("no ToF sensor found")
        self.distanceSens=VL53LOX(ic2)
        self.distanceSens.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
        self.distanceSens.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
        self.distanceSens.start()
    def read_distance(self):
        reading=distanceSens.read()
        return reading