from machine import Pin, PWM, ADC
from time import ticks_diff, ticks_ms, sleep

MIN_DUTY=1638
MAX_DUTY=8192

class servoMotor:
    def __init__(self, cal_table, servo_pin, feedback_pin, start_angle=0):
        self.pwm=PWM(Pin(servo_pin))
        self.pwm.freq(50)
        self.adc=ADC(Pin(feedback_pin))
        self.table=cal_table
        self.rising=cal_table[-1][1]>cal_table[0][1]
        self.target=start_angle
        self.set_angle(start_angle)
        self.min_angle=0
        self.max_angle=270
        self.open_angle=270
        self.closed_angle=0
        self.min_pulse=500
        self.max_pulse=2500
        #Set a position straight away
    def set_angle(self, angle):
        angle=max(self.min_angle, min(max_angle, angle))
        pulse= self.min_pulse+ ((angle-self.min_angle)/(self.max_angle-self.min_angle)*(self.max_pulse-self.min_pulse))
        duty=int((pulse/20000)*65525)
        servo.duty_u16(duty)
    def read_adc():
        total =0
        for i in range (10):
            total+= feedback.read_u16()
        return total/10
    def read_servo_angle():
        adc_value=read_adc()
        for i in range (len(self.table)-1):
            angle0, adc0 = self.table[i]
            angle1, adc 1=self.table[i+1]
            if adc0<=adc_value<=adc1:
                angle = angle0 + ((adc_value - adc0) / (adc1 - adc0)) * (angle1 - angle0)
                return angle
        if adc_value<self.table[0][1]:
            angle0, adc0=self.table[0]
            angle1, adc1=self.table[1]
        else:
            angle0,adc0=self.table[-2]
            angle1, adc1=self.table[-1]
        return angle0 + ((adc_value - adc0) / (adc1 - adc0)) * (angle1 - angle0)
    def close_grabber():
        set_angle(self.closed_angle)
        #sleep
        actual_angle=read_servo_angle()

            
        