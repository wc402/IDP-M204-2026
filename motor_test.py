from machine import Pin, PWM
from utime import sleep

class Motor:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        
    def off(self):
        self.pwm.duty_u16(0)
        
    def Forward(self, speed=100):
        self.mDir.value(1)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

    def Reverse(self, speed=30):
        self.mDir.value(0)
        self.pwm.duty_u16(int(65535 * speed / 100))



if __name__ == "__main__":
    motorL = Motor(dirPin=4, PWMPin=5)
    motorR = Motor(dirPin=6, PWMPin=7)
    
    motorL.Forward(60)
    motorR.Forward(30)
    sleep(1)
    motorL.Forward(30)
    motorR.Forward(60)
    sleep(1)
    
    