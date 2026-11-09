from machine import Pin, PWM
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


if __name__ == "__main__":
    motorR = Motor(dirPin=4, PWMPin=5)   # right wheel
    motorL = Motor(dirPin=7, PWMPin=6)   # left wheel (dir/pwm swapped on this channel)
    SPEED = 60

    def pause():
        motorL.off(); motorR.off()
        sleep(0.5)

    try:
        print("Forward")
        motorL.Forward(SPEED); motorR.Forward(SPEED)
        sleep(1); pause()

        print("Backward")
        motorL.Reverse(SPEED); motorR.Reverse(SPEED)
        sleep(1); pause()

        print("Turn right (spin on the spot)")
        motorL.Forward(SPEED); motorR.Reverse(SPEED)
        sleep(1); pause()

        print("Turn left (spin on the spot)")
        motorL.Reverse(SPEED); motorR.Forward(SPEED)
        sleep(1); pause()

        print("Done")
    finally:
        motorL.off(); motorR.off()
    

    
    
