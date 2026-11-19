from machine import Pin, PWM, ADC, Timer
from time import ticks_ms, ticks_diff
from motor import Motor
from distance_sensor import ToF

## Calibration constants
BASESPEED=70
STEP=1 
MAXSTEER=20
HALL_LIMIT=0 #Value above which a package is determined to contain a magnet(calibrate)
HALL_DISTANCE=0#Distance at which Hall reading is taken (calibrate)
GRAB_DISTANCE =0#Distance at which Hall reading is taken (calibrate)
DEBOUNCE = 200 #Debouncing delay (ms)
JUNCTION_LOOPS=5 #Number of times a junction must be detected before it can be acted upon (calibrate)
CLEAR_LOOPS=5 #Number of times outer sensors must be clear for before a new junction can be detected (Calibrate)
LEFT_TURN_TIMEOUT=950
RIGHT_TURN_TIMEOUT=950
SPIN_TIMEOUT=1900 #SPIN is a 180 degrees turn
## Define states
(IDLE, FOLLOW_LINE, AT_JUNCTION, TURNING, DETECTING_PACKAGE, GRABBING, RELEASING, PARKING,)=range(8)
STATE_NAMES = ("IDLE", "FOLLOW_LINE", "AT_JUNCTION", "TURNING",
               "DETECTING_PACKAGE", "GRABBING", "RELEASING", "PARKING")
STRAIGHT, LEFT, RIGHT, SPIN, COLLECT, DROP, PARK = range(7) 
## Define routes
route=[STRAIGHT,STRAIGHT,STRAIGHT]
## Set up robot
class Robot:
    def __init__(self):
        ## Set up I/O components
        self.lineSensFL=Pin(20, Pin.IN, Pin.PULL_DOWN)
        self.lineSensML=Pin(22, Pin.IN, Pin.PULL_DOWN)
        self.lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN)
        self.lineSensFR=Pin(16, Pin.IN, Pin.PULL_DOWN)
        self.motorR=Motor(dirPin=4, PWMPin=5)
        self.motorL=Motor(dirPin=7, PWMPin=6)
        self.motorServo=None
        self.buttonSS=Pin(17, Pin.IN, Pin.PULL_DOWN)
        self.LEDY=Pin(11, Pin.OUT) #LEDs
        self.LEDR=Pin(10, Pin.OUT)
        self.LEDG=Pin(12, Pin.OUT)
        #self.distanceSens=ToF()
        self.hallSens=None
        self.IRSens=None
        self.torqueSens=None
        self.buttonSS.irq(trigger=Pin.IRQ_RISING, handler=self.on_button)
        
        ## Add torque, hall, IR sensors; servo motor
        
        ## Initialise task variables
        self.steer = 0
        self.last_error = 0
        self.state=IDLE
        self.state_start=ticks_ms() #Will be used to determine time elapsed in each state
        self.stop= True #Triggered by the start/stop button
        self.last_press=0 # For debouncing
        self.reset = False #Has the AGV reset itself after entering IDLE/STOPPED
        self.route_step=0
        self.junction_count=0 # Used to ensure a junction has been detected mutliple times before it is acted on
        self.clear_count=0 #Used to ensure the AGV has passed a junction before it can act on another
        self.act= False
        self.turn= LEFT #Default, can change
        self.carrying=False
        self.polarity=None
        self.flashTimer=Timer()
        self.yellowOn=False
        self.lastprint=0
        
        ## Dictionary to match states to executable functions
        self.handlers = {
            IDLE: self.run_idle,
            FOLLOW_LINE: self.run_follow_line,
            AT_JUNCTION: self.run_at_junction,
            TURNING: self.run_turning,
            #DETECTING_PACKAGE: self.run_detecting,
            #GRABBING: self.run_grabbing,
            RELEASING: self.run_releasing,
            PARKING: self.run_parking}
        ## Add button and LED functionality (have flash at ~2Hz)
        
    def on_button(self,pin):
        now=ticks_ms()
        if ticks_diff(now, self.last_press) < DEBOUNCE:
            return
        self.last_press=now
        if self.state is IDLE:
            self.stop=False
        else:
            self.motorR.off()
            self.motorL.off()
            self.stop=True
            #debounce button, set the stop flag, turn motors off
            #needs both start and stop functionality
            pass
    def toggle_yellow(self, timer):
        self.LEDY.toggle()
    def set_yellow(self, on):
        if on and not self.yellowOn:
            self.flashTimer.init(freq=4, mode=Timer.PERIODIC, callback=self.toggle_yellow)
            self.yellowOn=True
        elif not on and self.yellowOn:
            self.flashTimer.deinit()
            self.yellowOn=False
            self.LEDY.value(0)
    def change_state(self, new_state):
        self.state=new_state
        self.state_start=ticks_ms()
        print("Now " + STATE_NAMES[new_state])
            
        if new_state== IDLE:
            self.motorR.off()
            self.motorL.off()
            self.steer, self.last_error, self.route_step, self.junction_count, self.clear_count, =0,0,0,0,0
            self.polarity=None
            self.act, self.carrying = False, False
            self.turn=LEFT
            self.set_yellow(False)
                ## Reset route/route_step/flags when entering IDLE
        else:
            self.set_yellow(True)
            pass
        if new_state == FOLLOW_LINE:
            self.steer=0
            self.last_error=0
            self.junction_count=0
        elif new_state == TURNING:
            self.junction_count=0
            self.clear_count=0
        elif new_state== GRABBING:
            pass #start engaging grabber
        elif new_state==RELEASING:
            pass #start opening grabber
    #def timed_out(self, limit_ms):
     #   if ticks_diff(ticks_ms(), self.state_start)>limit_ms:
      #      self.change_state(IDLE)
        # Main function to run. Should not contain any sleeps/blockimg
    def run(self):
        while True:
            if ticks_diff(ticks_ms(), self.lastprint) > 200:
                self.lastprint = ticks_ms()
                print(self.lineSensFL.value(), self.lineSensML.value(),
                      self.lineSensMR.value(), self.lineSensFR.value(),
                      self.act, self.clear_count, self.junction_count)
            if self.stop and self.state is not IDLE: #Checks for an emergency stop
                self.change_state(IDLE)
            self.handlers[self.state]() #runs current state once
        # Executed when idle
    def run_idle(self):
        if self.stop==False:
            self.change_state(AT_JUNCTION)
        # Executed to follow a straight line
    def run_follow_line(self): #Junction decision making has changed, straight line following has not
        error= self.lineSensML.value()-self.lineSensMR.value()
        if error !=0: #Robot off centre but still detecting line (only one sensor on). Correction grows with each step
            self.last_error=error
            self.steer-=error*STEP
        elif self.lineSensML.value()==0 and self.lineSensMR.value()==0: #Line lost (both sensors off)
            self.steer+=self.last_error*STEP #Keep turn in the opposite direction as when a line last detected
        else: #Following line correctly, do nothing
            self.steer = 0
        if self.act:  
            if self.lineSensFL.value()==1 or self.lineSensFR.value()==1:
                self.junction_count+=1
                self.clear_count=0
            if self.junction_count>=JUNCTION_LOOPS:
                self.change_state(AT_JUNCTION)
        elif not self.act:
            if self.lineSensFL.value()==0 and self.lineSensFR.value()==0:
                 self.clear_count+=1
                 self.junction_count=0
            if self.clear_count>=CLEAR_LOOPS:
                self.act=True
        self.steer=max(-MAXSTEER, min(MAXSTEER, self.steer))
        self.motorR.Forward(BASESPEED-self.steer)
        self.motorL.Forward(BASESPEED+self.steer)
    # Executed to move forward straight, without decision making component at junctions. Used for turns, grabbing and detecting
    def run_move_straight(self):
        error= self.lineSensML.value()-self.lineSensMR.value()
        if error !=0: #Robot off centre but still detecting line (only one sensor on). Correction grows with each step
            self.last_error=error
            self.steer-=error*STEP
        elif self.lineSensML.value()==0 and self.lineSensMR.value()==0: #Line lost (both sensors off)
            self.steer+=self.last_error*STEP #Keep turn in the opposite direction as when a line last detected
        else: #Following line correctly, do nothing
            self.steer = 0
        self.steer=max(-MAXSTEER, min(MAXSTEER, self.steer))
        self.motorR.Forward(BASESPEED-self.steer)
        self.motorL.Forward(BASESPEED+self.steer)
        # Executed to perform decision making at junctions
    def run_at_junction(self):
        self.route_step+=1
        if self.route_step==len(route):
            print("end route")
            self.change_state(IDLE)
        else:
            action=route[self.route_step]
            self.act=False
            if action==STRAIGHT:
                self.change_state(FOLLOW_LINE)
            elif action in (LEFT, RIGHT, SPIN):
                self.turn=action
                self.change_state(TURNING)
            elif action == COLLECT:
                self.change_state(DETECTING_PACKAGE)
            elif action== PARK:
                self.change_state(PARKING)
        # Exectuted to perform turns
    def run_turning(self):
        finished_turning=False
        action=self.turn
        if self.route_step>len(route):
            self.change_state(IDLE)
        if ticks_diff(ticks_ms(),self.state_start)<500:
            self.run_move_straight()
        else:
            if action==RIGHT:
                if ticks_diff(ticks_ms(), self.state_start)<RIGHT_TURN_TIMEOUT:
                    self.motorR.Reverse(BASESPEED)
                    self.motorL.Forward(BASESPEED)
                else:
                    finished_turning=True
            elif action==LEFT:
                if ticks_diff(ticks_ms(), self.state_start)<LEFT_TURN_TIMEOUT:
                    self.motorL.Reverse(BASESPEED)
                    self.motorR.Forward(BASESPEED)
                else:
                    finished_turning=True
            elif action==SPIN:
                if ticks_diff(ticks_ms(), self.state_start)<SPIN_TIMEOUT:
                    self.motorL.Reverse(BASESPEED)
                    self.motorR.Forward(BASESPEED)
                else:
                    finished_turning=True
            if finished_turning:
                if action==STRAIGHT:
                   self.change_state(FOLLOW_LINE)
                elif action==DROP:
                    self.route_step+=1
                    self.change_state(RELEASING)
                elif action==PARK:
                    self.route_step+=1
                    self.change_state(PARKING)
    #def run_detecting(self):
     #   if self.distanceSens.read_distance()<HALL_DISTANCE:
      #      self.run_move_straight()
       # elif self.distanceSens.read_distance()>=HALL_DISTANCE:
        #    self.motorR.off()
         #   self.motorL.off()
          #  if abs(self.hallSens.value())>HALL_LIMIT:
           #     self.change_state(GRABBING)
            #else:
             #   self.change_state(TURNING)
   # def run_grabbing(self):
    #    if self.distanceSens.read_distance()<GRAB_DISTANCE:
     #       self.run_move_straight()
      #  elif self.distanceSens.read_distance()>=GRAB_DISTANCE:
            #Engage grabber-complete when more known
       #     self.change_state(TURNING)
    def run_releasing(self):
        #Complete when more known
        #Will it be possible to spin here or is a reverse needed?
        pass
    def run_parking(self):
        #complete later
        pass
    ##Add flashing lights
if __name__=="__main__":
    robot=Robot()
    robot.run()
            
            

                
                
            
        
        
        
        
