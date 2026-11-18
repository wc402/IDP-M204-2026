from machine import Pin, PWM

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
        self.mDir.value(0)                 # 0 = forward on both channels
        self.pwm.duty_u16(int(65535 * speed / 100))

    def Reverse(self, speed=30):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * speed / 100))