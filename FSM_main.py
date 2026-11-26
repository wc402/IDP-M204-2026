from machine import Pin, PWM, ADC, Timer
from time import ticks_ms, ticks_diff, sleep_ms
from motor import Motor
from distance_sensor import ToF
from hall_sensor import hallSens, NORTH, SOUTH, NONE
from servo_motor import servoMotor
from IR_sensor import IRSens

## Calibration constants
BASESPEED=85 #Initial motor speed (both motors, pwm %)
SEARCHSPEED=50 #Speed for final, untimed turn segement (pwm%)
STEP=1 #Error multiplication factor for line following control
MAXSTEER=20 #Maximum additional steering for path correction (pwm%)
HALL_THRESHOLD=15 #Change in reading required for a magnet to be deemed present(mV, CALIBRATE)
HALL_DISTANCE=30 #Distance at which Hall reading is taken to determine the polarity of a package (mm, CALIBRATE)
PACKAGE_DISTANCE=350 #Distance sensor reading below which a package is determined to be in a bay (mm, CALIBRATE)
HALL_SETTLE=100 #time delay before taking a hall sensor reading)(ms)
GRAB_DISTANCE =50#Distance at which grabber is engaged (CALIBRATE)
DEBOUNCE = 500 #Debouncing delay for button(ms)
JUNCTION_LOOPS=10 #Number of times a junction must be detected before it can be acted upon
CLEAR_LOOPS=10 #Number of times outer sensors must be clear for before a new junction can be detected
TIMEOUT90=900 #ms for initial, timed segment of 90 degree turn
TIMEOUT_SPIN=2000 #ms for initial, timed segment of 180 degree turn
TIMEOUT_FORWARD=600 # time to move wheels forward onto junction for a turn (ms)
TIMEOUT_DETECTION=3000 #Time limit for a detection (unused)

SERVO_GRAB_CAL_TABLE = [ #Used to calibrate servo motors
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

## State definition
(STOPPED, IDLE, FOLLOW_LINE, AT_JUNCTION, REVERSING, TURNING, DETECTING_PACKAGE, GRABBING, RELEASING, PARKING, WAITING)=range(11) #Possible states
STATE_NAMES = ("STOPPED", "IDLE", "FOLLOW_LINE", "AT_JUNCTION", "REVERSING",
               "TURNING", "DETECTING_PACKAGE", "GRABBING", "RELEASING", "PARKING") #Used for debugging print statements
STRAIGHT, LEFT, RIGHT, SPIN, COLLECT, DROP, PARK, REVERSE, WAIT = range(9) #Possible route actions
## Test route
route=[STRAIGHT, LEFT, COLLECT, RIGHT, STRAIGHT, STRAIGHT, RIGHT]
##route=[STRAIGHT,LEFT]

## Robot class
class Robot:
    def __init__(self):
        ## Set up I/O components
        self.lineSensFL=Pin(20, Pin.IN, Pin.PULL_DOWN) #MR connection
        self.lineSensML=Pin(22, Pin.IN, Pin.PULL_DOWN) #ML connection
        self.lineSensMR=Pin(26, Pin.IN, Pin.PULL_DOWN) #FL connection
        self.lineSensFR=Pin(16, Pin.IN, Pin.PULL_DOWN) #FR connection
        self.motorR=Motor(dirPin=4, PWMPin=5)
        self.motorL=Motor(dirPin=7, PWMPin=6)
        self.motorServoGrab=servoMotor(SERVO_GRAB_CAL_TABLE, 15, 27,80)
        self.motorServoLift=servoMotor(SERVO_GRAB_CAL_TABLE, 13, 27,0)
        self.buttonSS=Pin(17, Pin.IN, Pin.PULL_DOWN)
        self.LEDY=Pin(11, Pin.OUT) #LEDs
        self.LEDR=Pin(10, Pin.OUT) #NEED LEDY=11, LEDR=10 FOR ACTUAL RUN
        self.LEDG=Pin(12, Pin.OUT)
        self.distanceSens=ToF()
        self.hallSens=hallSens(pin=28, threshold_mv=HALL_THRESHOLD)
        self.IRSens=IRSens(ir_pin=14)
        
        self.hallSens.calibrate_hallSens()
        ## Initialise variables for executing route actions
        self.steer = 0
        self.last_error = 0
        self.state=IDLE
        self.state_start=ticks_ms() #Will be used to determine time elapsed in each state
        self.pressed= False #Triggered by the start/stop button
        self.last_press=0 # For debouncing
        self.route_step=0
        self.junction_count=0 # Used to ensure a junction has been detected mutliple times before it is acted on
        self.clear_count=0 #Used to ensure the AGV has passed a junction before it can act on another
        self.act= False
        self.turn= LEFT #Default, can change
        self.polarity=None
        self.flashTimer=Timer()
        self.yellowOn=False
        self.lastprint=0
        self.finished_turning=False
        self.finished_timed_turn=False
        self.turn_correctionFR=False
        self.turn_correctionFL=False
        self.grabbing=False
        self.LEDY.value(0)
        self.LEDR.value(0)
        self.LEDG.value(0)
        
        ## Dictionary to match states to executable functions
        self.handlers = {
            STOPPED: self.run_stopped,
            IDLE: self.run_idle,
            FOLLOW_LINE: self.run_follow_line,
            AT_JUNCTION: self.run_at_junction,
            REVERSING: self.run_reversing,
            TURNING: self.run_turning,
            DETECTING_PACKAGE: self.run_detecting,
            GRABBING: self.run_grabbing,
            RELEASING: self.run_releasing,
            PARKING: self.run_parking,
            WAITING: self.run_waiting}
        
        self.buttonSS.irq(trigger=Pin.IRQ_RISING, handler=self.on_button)

    def on_button(self,pin):
        now=ticks_ms()
        if ticks_diff(now, self.last_press) < DEBOUNCE: #Debounces button press
            return
        self.last_press=now
        if self.state != IDLE and self.state != STOPPED:
            self.motorR.off()
            self.motorL.off()
        self.pressed=True
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
        #print("Now " + STATE_NAMES[new_state])
        if self.state == WAITING:        # leaving WAITING
            self.IRSens.close()
        if new_state==STOPPED:
            self.motorR.off()
            self.motorL.off()
            self.set_yellow(False)
            self.LEDY.value(1)
            self.LEDG.value(0)
            self.LEDR.value(0)
        if new_state== IDLE:
            self.motorR.off()
            self.motorL.off()
            self.steer, self.last_error, self.route_step, self.junction_count, self.clear_count =0,0,0,0,0
            self.polarity=None
            self.act = False
            self.turn=LEFT
            self.set_yellow(False)
            self.LEDY.value(1)
            self.LEDG.value(0)
            self.LEDR.value(0)
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
            self.polarity=None
        elif new_state == WAITING:
            self.IRSens.start()
    #def timed_out(self, limit_ms):
     #   if ticks_diff(ticks_ms(), self.state_start)>limit_ms:
      #      self.change_state(IDLE)
        # Main function to run. Should not contain any sleeps/blockimg
    def handle_button(self):
        if not self.pressed: #Nothing happens if button not pressed
            return
        self.pressed=False
        if self.state == IDLE: #First press puts AGV into STOPPED state, second into IDLE to allow AGV to restart route
            self.change_state(AT_JUNCTION)
        elif self.state == STOPPED:
            self.change_state(IDLE)
        else:
            self.change_state(STOPPED)
    def run(self):
        #Function called for the AGV to perform the tasks, checks state once per clock cycle and performs the relevant action
        while True:
            self.handle_button()
            self.handlers[self.state]()
        # Executed when idle
    def run_stopped(self):
        pass #Does nothing when stopped
    def run_idle(self):
        pass
    def run_follow_line(self):
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
    #Reversing with junction detection
    def run_reversing(self):
        error=self.lineSensML.value()-self.lineSensMR.value()
        if error !=0:
            self.lastError=error
            self.steer-=error*STEP
        else:
            self.steer=0
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
        self.motorR.Reverse(BASESPEED+self.steer)
        self.motorL.Reverse(BASESPEED-self.steer)
    #Reversing without junction detection
    def run_move_backwards(self):
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
            self.change_state(STOPPED)
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
            elif action == WAIT:
                self.change_state(WAITING)
        # Exectuted to perform turns
    def run_turning(self):
        action=self.turn
        if action==SPIN: #Performs 180 degree turn without moving forward first
            if ticks_diff(ticks_ms(), self.state_start)<TIMEOUT_SPIN:
                self.motorL.Reverse(BASESPEED)
                self.motorR.Forward(BASESPEED)
            else:
                self.finished_timed_turn=True
                
        #LEFT OR RIGHT TURN, without timers        
        else:
            if ticks_diff(ticks_ms(),self.state_start)<TIMEOUT_FORWARD: #Moves forward until wheels are on the junction
                self.run_move_straight()
                return
            if action==RIGHT: #Performs a right turn
                if self.lineSensFL.value() == 1: # TURNED TOO FAR, correct by turning left
                    self.motorR.Forward(SEARCHSPEED)
                    self.motorL.Reverse(SEARCHSPEED)
                elif self.lineSensML.value() == 1: # TURNED ENOUGH
                    self.finished_turning = True
                elif (self.lineSensFR.value() == 1 or self.lineSensMR.value() == 1): #slow search, keep turning
                    self.motorR.Reverse(SEARCHSPEED)
                    self.motorL.Forward(SEARCHSPEED)
                else: # Initial faster turn
                    self.motorR.Reverse(BASESPEED)
                    self.motorL.Forward(BASESPEED)
            elif action == LEFT: #Performs a left turn
                if self.lineSensFR.value() == 1: # TURNED TOO FAR, correct by turning right
                    self.motorL.Forward(SEARCHSPEED)
                    self.motorR.Reverse(SEARCHSPEED)
                elif self.lineSensMR.value() == 1: # TURNED ENOUGH
                    self.finished_turning = True
                elif (self.lineSensFL.value() == 1 or self.lineSensML.value() == 1): #slow search, keep turning
                    self.motorL.Reverse(SEARCHSPEED)
                    self.motorR.Forward(SEARCHSPEED)
                else: # Initial faster turn when none of sensors on
                    self.motorL.Reverse(BASESPEED)
                    self.motorR.Forward(BASESPEED)

        if self.finished_turning: #Once finished turning, moves into the next required state
            if self.route_step>=len(route): ### --------------------------------------- deleted +1 and need to check 
                self.change_state(STOPPED)
                return
            action=route[self.route_step]
            if action==STRAIGHT:
                self.change_state(FOLLOW_LINE)
            elif action==DROP:
                self.route_step+=1
                self.change_state(RELEASING)
            elif action==COLLECT: #for testing only
                self.route_step+=1
                self.change_state(DETECTING_PACKAGE)
            elif action==PARK:
                self.route_step+=1
                self.change_state(PARKING)
            elif action == WAIT:
                self.route_step+=1
                self.change_state(WAITING)
    def run_detecting(self):
        if (ticks_diff(ticks_ms(), self.state_start)<1000): #Moves forward into the bay to allow a reliable ToF reading
            self.run_move_straight()
        else:
            self.motorR.off()
            self.motorL.off()
            distance=self.distanceSens.read_distance()
            if (distance < PACKAGE_DISTANCE) and (distance > HALL_DISTANCE): #If a package is present, moves forward to allow a hall sensor reading
                self.run_move_straight()
            elif (distance < PACKAGE_DISTANCE) and (distance <HALL_DISTANCE): #Takes hall sensor reading at appropriate distance if package present
                self.motorR.off()
                self.motorL.off()
                self.polarity=self.hallSens.package_polarity()
            else distance > PACKAGE_DISTANCE: #Reverses out of bay if no package present
                self.route_step +=1 #Assumes next route step hard coded into route, will depend on navigation implementation
                self.change_state(REVERSING) #Will need to reverse regardless of navigation decisions
            if self.polarity is not None: #Package is magnetic so need to grab it
                self.change_state(GRABBING)
            else: #Package is a dummy, see same reasoning as above
                self.route_step+=1
                self.change_state(REVERSING)
    def run_grabbing(self):
        #Robot should already be stationary and at the grab distance (can/should be the same as the hall sensor reading distance)
        if ticks_diff(ticks_ms(), self.state_start)<2000:
            self.motorServoGrab.set_angle(0)
        if ticks_diff(ticks_ms(), self.state_start+2000)<2000:
            self.motorServoLift.set_angle(0)
        if self.polarity == NORTH:
            self.LEDR.value(1)
            print("NORTH")
        elif self.polarity== SOUTH:
            self.LEDG.value(1)
             print("SOUTH")
        if ticks_diff(ticks_ms(), self.state_start+4000)<2000:
            self.motorServoLift.set_angle(30)
        else:
            self.route_step+=1
            self.change_state(REVERSING)
 
    def run_releasing(self):
        if ticks_diff(ticks_ms(), self.state_start)<2000:
            print("opening")
            self.motorServoLift.set_angle(15)
            self.motorServoGrab.open_grabber()
            self.LEDR.value(0)
            self.LEDG.value(0)
        else:
            self.change_state(REVERSING)
    def run_parking(self):
        #complete later
        self.change_state(STOPPED)
        return
    def run_waiting(self):
        print("Detecting")
        self.motorR.off()
        self.motorL.off()
        self.IRSens.update()
        if self.IRSens.detected():
            print("--Detected--")
            self.change_state(FOLLOW_LINE)
            
    def test_servo(self):
        self.motorServoLift.set_angle(0)
        self.motorServoGrab.set_angle(0)
        sleep_ms(600)
        self.motorServoGrab.set_angle(80)
        self.motorServoLift.set_angle(15)
        sleep_ms(600)
        self.motorServoGrab.set_angle(80)
        self.motorServoLift.set_angle(15)

        ##self.motorServoGrab.close_grabber(10)
    ##Add flashing lights
if __name__=="__main__":
    robot=Robot()
    robot.test_servo()
    robot.run()
            
            

                
                
            
        
        
        
        
















                
                
            
        
        
        
        














