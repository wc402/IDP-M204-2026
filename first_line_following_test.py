from machine import Pin
from utime import sleep

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


if name == "__main__":
    motorR = Motor(dirPin=4, PWMPin=5)   # right wheel
    motorL = Motor(dirPin=7, PWMPin=6)   # left wheel (dir/pwm swapped on this channel)
    left      = Pin(19, Pin.IN, Pin.PULL_DOWN)   # GP19 = header pin 25
    right     = Pin(20, Pin.IN, Pin.PULL_DOWN)   # GP20 = header pin 26
    
    for i in range(10):
        if left:
            motorL.Forward(30)
            motorR.Forward(60)
        elif right:
            motorR.Forward(60)
            motorL.Forward(30)
        elif left&right:
            motorR.Reverse(30)
            motorL.Reverse(30)
        else:
            motorR.Forward(50)
            motorL.Forward(50)
        sleep(1)
        
        

