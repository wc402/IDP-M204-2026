# tof_motor_test.py
# Drive both wheels forward; stop when the ToF sensor sees something close;
# go again when the way is clear. Prints the distance as it runs.
#
# No button: it starts as soon as you press Run. Stop it with Thonny's Stop.
#
# Works with either course ToF sensor - it checks which one is plugged in:
#   VL53L0X            (I2C address 0x29)
#   TMF8701 / TMF8801  (I2C address 0x41)
#
# Wiring (same pins as the course test files):
#   VCC -> 3V3      GND -> GND
#   SDA -> GP8 (header pin 11)      SCL -> GP9 (header pin 12)
#
# Needs the course "libs" folder on the Pico.

from machine import Pin, PWM, I2C
from utime import sleep, sleep_ms, ticks_ms, ticks_diff

STOP_MM = 100          # stop when something is closer than this
GO_MM = 130            # drive again once it is further away than this
SPEED = 40             # motor speed, percent
TMF_MODEL = "TMF8701"  # only used for the TMF sensor: "TMF8701" or "TMF8801"

FAR = 9999             # stands for "nothing in range"


class Motor:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)
        self.pwm = PWM(Pin(PWMPin))
        self.pwm.freq(1000)
        self.off()

    def off(self):
        self.pwm.duty_u16(0)
        self.mDir.value(0)

    def Forward(self, speed=100):
        self.mDir.value(0)   # 0 = forward on both channels
        self.pwm.duty_u16(int(65535 * speed / 100))

    def Reverse(self, speed=30):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * speed / 100))


def make_sensor():
    """Find the ToF sensor and return a function that reads it.

    The returned function gives: a distance in mm, FAR if nothing is in
    range, or None if there is no new reading yet.
    """
    i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)   # I2C0 on GP8 & GP9
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
            d = tof.read()                  # waits for the next measurement
            return d if d < 2000 else FAR   # about 8190 means nothing in range
        return read_mm

    if 0x41 in found:
        from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8701, DFRobot_TMF8801
        if TMF_MODEL == "TMF8701":
            tof = DFRobot_TMF8701(i2c_bus=i2c)
        else:
            tof = DFRobot_TMF8801(i2c_bus=i2c)

        tries = 0
        while tof.begin() != 0:
            tries += 1
            if tries >= 10:
                raise RuntimeError("TMF sensor would not start - check TMF_MODEL and that libs/DFRobot_TMF8x01/fw is on the Pico")
            sleep(0.5)
        print("Sensor reports:", tof.get_sensor_model(), "(TMF_MODEL is set to " + TMF_MODEL + ")")

        if TMF_MODEL == "TMF8701":
            # eCOMBINE = 0 to 60 cm (the course test uses ePROXIMITY, which is only 0 to 10 cm)
            tof.start_measurement(calib_m=tof.eMODE_NO_CALIB, mode=tof.eCOMBINE)
        else:
            tof.start_measurement(calib_m=tof.eMODE_NO_CALIB)

        def read_mm():
            if not tof.is_data_ready():
                return None                 # no new reading yet
            d = tof.get_distance_mm()
            return d if d > 0 else FAR      # 0 means nothing in range
        return read_mm

    raise RuntimeError("No ToF sensor found on GP8/GP9 - check the four wires")


if __name__ == "__main__":
    motorR = Motor(dirPin=4, PWMPin=5)   # right wheel
    motorL = Motor(dirPin=7, PWMPin=6)   # left wheel

    read_mm = make_sensor()
    print("Running - press Stop in Thonny to finish.")

    driving = False            # stays stopped until the sensor says the way is clear
    shown = None
    last_reading = ticks_ms()
    last_print = ticks_ms()

    try:
        while True:
            d = read_mm()
            now = ticks_ms()
            quiet = False

            if d is not None:
                last_reading = now
                shown = d
                if d < STOP_MM:
                    driving = False
                elif d > GO_MM:
                    driving = True
            elif ticks_diff(now, last_reading) > 500:
                driving = False            # sensor has gone quiet: stop to be safe
                quiet = True

            if driving:
                motorL.Forward(SPEED)
                motorR.Forward(SPEED)
            else:
                motorL.off()
                motorR.off()

            if ticks_diff(now, last_print) > 250:
                last_print = now
                if quiet:
                    text = "no reading from the sensor"
                elif shown is None:
                    text = "waiting for a reading"
                elif shown == FAR:
                    text = "nothing in range"
                else:
                    text = str(shown) + " mm"
                print("GO  " if driving else "STOP", text)

            sleep_ms(10)
    finally:
        motorL.off()
        motorR.off()
        print("Motors off")