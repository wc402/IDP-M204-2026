from machine import Pin, disable_irq, enable_irq
from time import ticks_ms, ticks_diff

class IRSens:
    def __init__(self, ir_pin, window_ms=2000, min_pulses=105):
        #Note that output is active low
        self.pin=Pin(ir_pin, Pin.IN, Pin.PULL_UP)
        self.window_ms=window_ms
        self.min_pulses=min_pulses
        self.start_time=ticks_ms()
        self.seen = False
        self.count=0
        self.pulses=0
    def start(self):
        ##Begins detecting IR pulses
        self.count=0
        self.pulses=0
        self.seen=False
        self.window_start=ticks_ms()
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.on_edge)
    def on_edge(self, pin):
        self.count+=1 #Counts an IR pulse each time the output falls from 1 to 0
    def update(self):
        now=ticks_ms()
        if ticks_diff(now, self.start_time) >= self.window_ms:
            state=disable_irq()
            n=self.count
            self.count=0
            enable_irq(state)
            self.pulses=n
            self.seen = n >=self.min_pulses
            self.start_time=now
        return self.seen
    def detected(self):
        #Returns true if the last full window contained enough IR pulses
        print(self.seen)
        return self.seen
    def close(self):
        #Stop counting and disable the pin interrupt
        self.pin.irq(handler=None)

        
