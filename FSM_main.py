from machine import Pin, PWM, ADC, Timer
from time import ticks_ms, ticks_diff
from motor import Motor
from distance_sensor import ToF
from hall_sensor import hallSens, NORTH, SOUTH, NONE
from servo_motor import servoMotor
## Calibration constants
BASESPEED=70
SEARCHSPEED=50
STEP=1 
MAXSTEER=20
HALL_THRESHOLD=15 #Change in reading required for a magnet to be deemed present(mV, )
HALL_DISTANCE=0#Distance at which Hall reading is taken (calibrate)
HALL_SETTLE=100 #time delay before taking a hall sensor reading )(ms)
GRAB_DISTANCE =50#Distance at which grabber is engaged (calibrate)
DEBOUNCE = 500 #Debouncing delay for button(ms)
JUNCTION_LOOPS=10 #Number of times a junction must be detected before it can be acted upon (calibrate)
CLEAR_LOOPS=10 #Number of times outer sensors must be clear for before a new junction can be detected (Calibrate)
TIMEOUT90=900 #ms for initial 90 degree turn (Calibrate)
TIMEOUT_SPIN=1800 #ms for initial 180 degree turn (Calibrate)
TIMEOUT_FORWARD=600 # time to move wheels forward onto junction for a turn
TIMEOUT_DETECTION=3000 #Timelimit for a detection

SERVO_GRAB_CAL_TABLE = [
    (0,   5332),
    (27,  11897),
    (54,  18960),
    (81,  26003),
    (108, 32781),
    (135, 39680),
    (162, 46165),
    (189, 51563),
    (216, 56142),
    (243, 60008),
    (270, 62970)
]

## Define states
(IDLE, FOLLOW_LINE, AT_JUNCTION, REVERSING, TURNING, DETECTING_PACKAGE, GRABBING, RELEASING, PARKING)=range(9) #Possible states
STATE_NAMES = ("IDLE", "FOLLOW_LINE", "AT_JUNCTION", "REVERSING",
               "TURNING", "DETECTING_PACKAGE", "GRABBING", "RELEASING", "PARKING")
STRAIGHT, LEFT, RIGHT, SPIN, COLLECT, DROP, PARK, REVERSING = range(8) #Possible route actions
## Define routes
route=[COLLECT,DROP]
## Set up robot
class Robot:
    def __init__(self):
        ## Set up I/O components
        self.lineSensFL=Pin(20, Pin.IN, Pin.PULL_DOWN) #MR connection
        self.lineSensML=Pin(22, Pin.IN, Pin.PULL_DOWN) #ML connection
        self.lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN) #FL connection
        self.lineSensFR=Pin(16, Pin.IN, Pin.PULL_DOWN) #FR connection
        self.motorR=Motor(dirPin=4, PWMPin=5)
        self.motorL=Motor(dirPin=7, PWMPin=6)
        self.motorServoGrab=servoMotor(SERVO_GRAB_CAL_TABLE, 15, 27)
        self.buttonSS=Pin(17, Pin.IN, Pin.PULL_DOWN)
        self.LEDY=Pin(11, Pin.OUT) #LEDs
        self.LEDR=Pin(10, Pin.OUT) #NEED LEDY=11, LEDR=10 FOR ACTUAL RUN
        self.LEDG=Pin(12, Pin.OUT)
        #self.distanceSens=ToF()
        #self.hallSens=hallSens(pin=28, threshold_mv=HALL_THRESHOLD)
        self.IRSens=None
        self.buttonSS.irq(trigger=Pin.IRQ_RISING, handler=self.on_button)
        
        ## Add hall, IR sensors; servo motor
        
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
        self.finished_turning=False
        self.finished_timed_turn=False
        self.turn_correctionFR=False
        self.turn_correctionFL=False
        self.grabbing=False
        
        ## Dictionary to match states to executable functions
        self.handlers = {
            IDLE: self.run_idle,
            FOLLOW_LINE: self.run_follow_line,
            AT_JUNCTION: self.run_at_junction,
            REVERSING: self.run_reversing,
            TURNING: self.run_turning,
            DETECTING_PACKAGE: self.run_detecting,
            GRABBING: self.run_grabbing,
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
            self.clear_count=0
        elif new_state == TURNING:
            self.junction_count=0
            self.clear_count=0
            self.finished_turning=False
            self.finished_timed_turn=False
            self.turn_correctionFR=False
            self.turn_correctionFL=False
        elif new_state== GRABBING:
            self.grabbing=False
        elif new_state==RELEASING:
            self.releasing=False
    #def timed_out(self, limit_ms):
     #   if ticks_diff(ticks_ms(), self.state_start)>limit_ms:
      #      self.change_state(IDLE)
        # Main function to run. Should not contain any sleeps/blockimg
    def run(self):
        while True:
            #if self.route_step==0:
                #hallSens.calibrate_hallSens()
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
    def run_reversing(self):
        error=self.lineSensML.value()-self.lineSensMR.value()
        if error !=0:
            self.lastError=error
            self.steer-=error*STEP
        else:
            self.steer=0
            self.steer=max(-MAXSTEER, min(MAXSTEER, self.steer))
        self.motorR.Reverse(BASESPEED+self.steer)
        self.motorL.Reverse(BASESPEED-self.steer)
    def run_at_junction(self):
        if self.route_step==len(route):
            self.change_state(IDLE)
        else:
            action=route[self.route_step]
            self.route_step+=1
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
        action=self.turn
        if action==SPIN: #Performs 180 degree turn without moving forward first
            if ticks_diff(ticks_ms(), self.state_start)<TIMEOUT_SPIN:
                self.motorL.Reverse(BASESPEED)
                self.motorR.Forward(BASESPEED)
            else:
                self.finished_timed_turn=True
        else:
            if ticks_diff(ticks_ms(),self.state_start)<TIMEOUT_FORWARD: #Moves forward until wheels are on the junction
                self.run_move_straight()
                return
            if action==RIGHT: #Performs an initial timed right turn
                if ticks_diff(ticks_ms(), (self.state_start+TIMEOUT_FORWARD))<TIMEOUT90:
                    self.motorR.Reverse(BASESPEED)
                    self.motorL.Forward(BASESPEED)
                else:
                    self.finished_timed_turn=True
            elif action==LEFT: #Performs an initial timed left turn
                if ticks_diff(ticks_ms(), (self.state_start+TIMEOUT_FORWARD))<TIMEOUT90:
                    self.motorL.Reverse(BASESPEED)
                    self.motorR.Forward(BASESPEED)
                else:
                    self.finished_timed_turn=True
        if self.finished_timed_turn:
            if self.lineSensFR.value()==1: #Is the far right sensor on? (case of over/under turn)
                self.turn_correctionFR=True
            elif self.lineSensFL.value()==1: #Is the far left sensor on? (case of over/under turn)
                self.turn_correctionFL=True
            else:
                self.finished_turning=True
        if self.turn_correctionFR==True: #If far right sensor is on, robot slowly turns until the middle left sensor is back on the line 
            if self.lineSensML.value()==0:
                self.motorR.Reverse(SEARCHSPEED)
                self.motorL.Forward(SEARCHSPEED)
            elif self.lineSensML.value()==1:
                self.turn_correctionFR=False
                self.finished_turning=True
        elif self.turn_correctionFL==True: #If far left sensor is on, robot slowly turns until the middle right sensor is back on the line
            if self.lineSensMR.value()==0: 
                self.motorR.Forward(SEARCHSPEED)
                self.motorL.Reverse(SEARCHSPEED)
            elif self.lineSensML.value()==1:
                self.turn_correctionFL=False
                self.finished_turning=True
        if self.finished_turning: #Once finished turning, moves into the next required state
            if self.route_step+1>=len(route):
                self.change_state(IDLE)
                return
            action=route[self.route_step]
            if action==STRAIGHT:
                self.change_state(FOLLOW_LINE)
            elif action==DROP:
                self.route_step+=1
                print("Changing to reease")
                self.change_state(RELEASING)
            elif action==COLLECT: #for testing only
                self.route_step+=1
                self.change_state(GRABBING)
            elif action==PARK:
                self.route_step+=1
                self.change_state(PARKING)
    def run_detecting(self):
        #if self.distanceSens.read_distance()<HALL_DISTANCE:
         #   self.run_move_straight()
        #elif self.distanceSens.read_distance()>=HALL_DISTANCE:
         #   self.motorR.off()
          #  self.motorL.off()
           # hallSens_reading=hallSens.package_polarity()
            #if hallSens_reading is NONE:
             #   print("no magnet")
            #elif hallSens_reading is NORTH:
             #   self.LEDR.value(1)
              #  self.change_state(GRABBING)
            #elif hallSens_reading is SOUTH:
             #   self.LEFL.value(1)
        self.change_state(GRABBING)
    def run_grabbing(self):
        #if self.distanceSens.read_distance()<GRAB_DISTANCE:
        if self.grabbing == False and ticks_diff(ticks_ms(), self.state_start)<2300:
            self.run_move_straight()
        #elif self.distanceSens.read_distance()>=GRAB_DISTANCE:
        elif self.grabbing == False:
            self.motorR.off()
            self.motorL.off()
            self.grabbing=True
            self.state_start=ticks_ms()
        if self.grabbing and ticks_diff(ticks_ms(), self.state_start)<2000:
            self.motorServoGrab.close_grabber()
        elif self.grabbing:
            self.turn=SPIN
            self.change_state(TURNING)
    def run_releasing(self):
        print('calling drop')
        self.motorServoGrab.open_grabber()
        self.change_state(IDLE)
    def run_parking(self):
        #complete later
        self.change_state(IDLE)
        return
    ##Add flashing lights
if __name__=="__main__":
    robot=Robot()
    robot.run()
            
            

                
                
            
        
        
        
        







