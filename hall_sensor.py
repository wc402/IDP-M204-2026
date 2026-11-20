from machine import Pin, ADC
from time import sleep_ms

NORTH =-1
NONE=0
SOUTH =1

BASE_MIN_MV=1590 #mV, lower limit for background field reading
BASE_MAX_MV=1710 #mV, upper limit for background field reading

class hallSens:
    def __init__ (self, pin=28, threshold_mv=15, swap_poles=False, samples=200):
        self.adc=ADC(Pin(pin))
        self.threshold_mv=threshold_mv
        self.swap=swap_poles
        self.samples=samples
        self.rest_mv=None
        self.last_change_mv=0
        self.calibrate()
    def read_hallSens_mv(self, samples=None):
        ## Averages many sample readings (mV)
        n=samples or self.samples
        total=0
        for i in range(n):
            total+=self.adc.read_u16()
        return total/n*3300/65535
    def calibrate_hallSens(self, readings=20, gaps_ms=50):
        # Measures background field. Call with motors off, away from magnets, and only on start-up
        total=0
        for i in range(readings):
            total+=self.read_mv
            sleep_ms(gap_ms)
        self.rest_mv=total/readings
        #if not (BASE_MIN_MV<=self.reset_mv<=BASE_MAX_MV):
        return self.rest_mv
    def package_polarity(self):
        diff=self.read_mv()-self.rest_mv
        if self.swap:
            diff=-diff
        self.last_change_mv=diff
        if diff >self.threshold_mv:
            return SOUTH
        if diff<-self.threshold_mv:
            return NORTH
        return NONE