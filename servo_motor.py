from machine import Pin, PWM, ADC

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
        self.set_angle(start_angle) #Set a position straight awat
    def set_angle(self, angle):
        self.target=max(0, min(270, angle))
        self.pwm.duty_u16(int(MIN_DUTY+self.target/270 *(MAX_DUTY-MIN_DUTY)))
    def read_volts(self, samples=20):
        total=0
        for _ in range(samples):
            total+=self.adc.read_u16()
        return total/samples*3.3/65535
    def read_angle(self):
        volts=read_volts(self)
        first, last = table[0][1], table[-1][1]
        if (self,rising and volts<=first) or (not rising and volts>=first): #below 0 degrees
            angle0, volts0=table[0]
            angle1, volts1=table[1]
            return angle0_(volts-volts0)/(volts1-volts0)*(angle1-angle0)
        for i in range(len(table-1)):
            angle0,volts0=table[i]
            angle1,volts1=table[i+1]
            lo, hi=(volts0, volts1) if self.rising else (volts1, volts0)
            last = (i==len(self.table)-2)
            if (lo<= volts <= hi) or (last and volts1 != volts0):
                if low <= v<=hi or last:
                    return angle0_(volts-volts0)/(volts1-volts0)*(angle1-angle0)
        return 0.0
    def at_target(self, tolerance=5):
        return abs(self.read_angle()-self.target)<tolerance
            
        