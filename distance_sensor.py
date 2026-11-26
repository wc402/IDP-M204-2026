from machine import Pin, PWM, I2C
from libs.VL53L0X.VL53L0X import VL53L0X

class ToF:
    def __init__(self, SDA=18, SCL=19):
        i2c = I2C(1, sda=Pin(SDA), scl=Pin(SCL), freq=100000)
        if 0x29 in i2c.scan():
            ##raise RuntimeError("no ToF sensor found")
            self.distanceSens=VL53L0X(i2c)
            self.distanceSens.set_Vcsel_pulse_period(self.distanceSens.vcsel_period_type[0], 18)
            self.distanceSens.set_Vcsel_pulse_period(self.distanceSens.vcsel_period_type[1], 14)
            self.distanceSens.start()
    def read_distance(self):
        reading=self.distanceSens.read()
        print(reading)
        return reading


