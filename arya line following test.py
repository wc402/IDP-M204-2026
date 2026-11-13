# arya_line_following.py
# Arya's line following, built on "arya line following test.py" (same pins, motor
# settings and speeds), changed for the new sensor layout.
#
# Four line sensors in a row across the front of the robot:
#   - the two INNER sensors sit ON the white line (both read 1 when centred)
#   - the two OUTER sensors sit just OUTSIDE it (they read 1 only at a junction)
#
# MODE = "check"   : wiring test. Laptop plugged in, wheels off the table.
#                    Centred on the line it should print 0 1 1 0.
# MODE = "follow"  : follow the line, drive straight over every junction and say
#                    which kind each one was. Use this to test the states.
# MODE = "advance" : tuning aid for ADVANCE_MS (see the route settings).
# MODE = "route"   : Monday's line test on the LEFT side of the table:
#                    start box -> rack line A1L -> Loading area 2 -> start box.
#
# No button: it starts as soon as you press Run (or at power-up if saved as main.py).
# PRINT must be False for battery runs: a print with no laptop reading it stalls the loop.
#
# ---------------------------------------------------------------------------------
# ALL 16 SENSOR STATES   (OL IL IR OR = outer left, inner left, inner right,
#                         outer right; 1 = white line, 0 = black)
#
#   OL IL IR OR   what it means                       what the robot does
#   0  1  1  0    centred on the line                 straight on
#   0  1  0  0    line a little to the left           steer left
#   0  0  1  0    line a little to the right          steer right
#   1  0  0  0    line far to the left                pivot left
#   0  0  0  1    line far to the right               pivot right
#   0  0  0  0    lost the line                       turn back towards the side the
#                                                     line was last seen on; stop if
#                                                     it is still lost after LOST_MS
#   1  1  1  0    junction on the LEFT                ]
#   1  1  0  0      (same, robot a bit off-centre)    ]
#   1  0  1  0      (same)                            ]
#   0  1  1  1    junction on the RIGHT               ]  drive straight over it,
#   0  0  1  1      (same)                            ]  unless the route says
#   0  1  0  1      (same)                            ]  "turn at this one"
#   1  1  1  1    line across BOTH sides              ]
#   1  0  1  1      (T-junction, crossing, box edge)  ]
#   1  1  0  1      (same)                            ]
#   1  0  0  1      (same)                            ]
#
# A junction is classified once the robot has passed it: "left", "right" or "both".
# The route counts junctions of one kind ("the 3rd right") and drives straight over
# the others, so lines it doesn't care about (box edges, other branches) can't
# throw the count out.
# ---------------------------------------------------------------------------------

from machine import Pin, PWM
from utime import sleep, sleep_ms, ticks_ms, ticks_diff

# ---------------- settings ----------------
MODE = "route"         # "check", "follow", "advance" or "route"
PRINT = True           # True on the laptop, False on battery
START_DELAY_S = 0      # seconds to wait before moving (0 = start instantly)

# Line sensors: 1 = white line, 0 = black
PIN_OUTER_LEFT = 28    # header pin 34
PIN_INNER_LEFT = 27    # header pin 32
PIN_INNER_RIGHT = 26   # header pin 31
PIN_OUTER_RIGHT = 22   # header pin 29

# Motors: copy these three from your working line_follow_4.py
SWAP_MOTORS = False    # True if "LEFT wheel" in the check spins the right-hand wheel
REVERSE_LEFT = False   # True if the left wheel runs backwards in the check
REVERSE_RIGHT = False  # True if the right wheel runs backwards in the check

BASE = 50              # straight-line speed, percent
SLOW = 30              # inside wheel when steering
FAST = 60              # outside wheel when steering
PIVOT = 55             # outside wheel when pivoting (the inside wheel stops)
TURN = 40              # both wheels when turning on the spot
LOST_MS = 2000         # stop if the line has been lost for this long

# ---------------- route settings ----------------
RACK = 1               # rack line to visit: 1 = A1L ... 6 = A6L (1 is the safest)
BAY = 2                # loading area to visit: 1 or 2
ADVANCE_MS = 1100      # after a junction is first seen, keep going this long before
                       # turning, so the WHEELS are over it. Tune with MODE = "advance".
RACK_MAX_S = 10        # back-up: stop on the rack line after this long even if its end
                       # wasn't seen. Set it just above the time it takes to get there.
BAY_MAX_S = 8          # same for the loading-area line
PAUSE_S = 2            # how long to stand still at the rack and at the loading area
FINISH_EXTRA_S = 1.0   # after the centre line in the start box, drive on this long
START_IGNORE_S = 1.5   # ignore junctions for this long at the start
HOME_FACTOR = 1.1      # back-up for the finish: stop after this x the first leg's time

QUIET_MS = 300         # after a turn, junctions are ignored for this long
CLEAR_MS = 60          # a junction is over once both outer sensors read black this long
END_MS = 40            # a line has ended once all four sensors read black this long
TURN_BLIND_MS = 200    # at the start of a turn, don't look at the sensors for this long
TURN_MAX_MS = 8000     # give up (stop) if a turn hasn't found the line by then
# ------------------------------------------


class Motor:
    def __init__(self, dirPin, PWMPin, reverse=False):
        self.mDir = Pin(dirPin, Pin.OUT)
        self.pwm = PWM(Pin(PWMPin))
        self.pwm.freq(1000)
        self.fwd = 1 if reverse else 0   # direction-pin value that means "forward"
        self.off()

    def off(self):
        self.pwm.duty_u16(0)
        self.mDir.value(0)

    def Forward(self, speed=100):
        self.mDir.value(self.fwd)
        self.pwm.duty_u16(int(65535 * speed / 100))

    def Reverse(self, speed=30):
        self.mDir.value(1 - self.fwd)
        self.pwm.duty_u16(int(65535 * speed / 100))


# (direction pin, speed pin) for each motor socket on the PicoBot
right_pins = (4, 5)
left_pins = (7, 6)
if SWAP_MOTORS:
    left_pins, right_pins = right_pins, left_pins

motorL = Motor(left_pins[0], left_pins[1], REVERSE_LEFT)
motorR = Motor(right_pins[0], right_pins[1], REVERSE_RIGHT)

outer_left = Pin(PIN_OUTER_LEFT, Pin.IN, Pin.PULL_DOWN)
inner_left = Pin(PIN_INNER_LEFT, Pin.IN, Pin.PULL_DOWN)
inner_right = Pin(PIN_INNER_RIGHT, Pin.IN, Pin.PULL_DOWN)
outer_right = Pin(PIN_OUTER_RIGHT, Pin.IN, Pin.PULL_DOWN)

t90 = None             # how long a quarter turn takes (measured on the first one)


def say(text):
    if PRINT:
        print(text)


def stop():
    motorL.off()
    motorR.off()


def drive(left, right):
    if left > 0:
        motorL.Forward(left)
    else:
        motorL.off()
    if right > 0:
        motorR.Forward(right)
    else:
        motorR.off()


def read():
    return outer_left.value(), inner_left.value(), inner_right.value(), outer_right.value()


class Follower:
    """Line following plus junction spotting. Call update() once per loop."""

    def __init__(self, ignore_ms=0):
        self.t0 = ticks_ms()
        self.ignore_ms = ignore_ms   # junctions are not looked for during this time
        self.last_side = 0           # where the line was last seen: -1 left, 0 middle, 1 right
        self.lost_since = None
        self.in_junction = False
        self.junction_start = 0
        self.first_hit = 0
        self.hits = 0
        self.saw_left = False
        self.saw_right = False
        self.black_since = None

    def update(self, ol, il, ir, orr):
        """Set the wheels from one sensor reading.

        Returns None, or (kind, start time) just after the robot has passed a
        junction. kind is "left", "right" or "both"; the start time is when it
        was first seen.
        """
        now = ticks_ms()
        junction = ((ol or orr) and (il or ir)) or (ol and orr)

        # Crossing a junction: drive straight, note which sides it is on.
        if self.in_junction:
            drive(BASE, BASE)
            if ol:
                self.saw_left = True
            if orr:
                self.saw_right = True
            if ol or orr:
                self.black_since = None
                return None
            if self.black_since is None:
                self.black_since = now
                return None
            if ticks_diff(now, self.black_since) < CLEAR_MS:
                return None
            self.in_junction = False
            self.last_side = 0
            if self.saw_left and self.saw_right:
                kind = "both"
            elif self.saw_left:
                kind = "left"
            else:
                kind = "right"
            return (kind, self.junction_start)

        # A new junction? It has to be seen twice in a row (filters out noise).
        if junction and ticks_diff(now, self.t0) >= self.ignore_ms:
            self.hits += 1
            if self.hits == 1:
                self.first_hit = now
            if self.hits >= 2:
                self.hits = 0
                self.in_junction = True
                self.junction_start = self.first_hit
                self.saw_left = bool(ol)
                self.saw_right = bool(orr)
                self.black_since = None
                drive(BASE, BASE)
                return None
        else:
            self.hits = 0

        # Ordinary line following - the states in the table at the top.
        if ol or il or ir or orr:
            self.lost_since = None
        if junction:                 # junction states: straight on
            drive(BASE, BASE)
        elif ol:                     # 1 0 0 0  line far to the left
            drive(0, PIVOT)
            self.last_side = -1
        elif orr:                    # 0 0 0 1  line far to the right
            drive(PIVOT, 0)
            self.last_side = 1
        elif il and ir:              # 0 1 1 0  centred
            drive(BASE, BASE)
            self.last_side = 0
        elif il:                     # 0 1 0 0  line a little to the left
            drive(SLOW, FAST)
            self.last_side = -1
        elif ir:                     # 0 0 1 0  line a little to the right
            drive(FAST, SLOW)
            self.last_side = 1
        else:                        # 0 0 0 0  lost
            if self.lost_since is None:
                self.lost_since = now
            elif ticks_diff(now, self.lost_since) > LOST_MS:
                stop()
                raise RuntimeError("lost the line")
            if self.last_side < 0:
                drive(0, PIVOT)
            elif self.last_side > 0:
                drive(PIVOT, 0)
            else:
                drive(SLOW, SLOW)
        return None


def drive_to(kind, count, ignore_ms=QUIET_MS, max_ms=None):
    """Follow the line until the count-th junction of this kind has been passed.

    kind: "left", "right", "both" or "any". Other kinds are driven straight over.
    Returns the time the matching junction was first seen, or None if max_ms ran out.
    """
    f = Follower(ignore_ms)
    seen = 0
    while True:
        result = f.update(*read())
        if result:
            say("  passed a junction: " + result[0])
            if kind == "any" or result[0] == kind:
                seen += 1
                if seen >= count:
                    return result[1]
        if max_ms is not None and ticks_diff(ticks_ms(), f.t0) >= max_ms:
            return None
        sleep_ms(1)


def drive_for(seconds):
    """Follow the line for a fixed time (junctions are driven straight over)."""
    f = Follower(int(seconds * 1000) + 1)
    while ticks_diff(ticks_ms(), f.t0) < seconds * 1000:
        f.update(*read())
        sleep_ms(1)


def drive_to_end(max_s, stop_at_edge):
    """Follow the line until it ends (all four sensors black for END_MS), or until a
    line across both outer sensors (the edge of a loading area) if stop_at_edge,
    or until max_s runs out. Then stop. Returns why it stopped."""
    f = Follower(int(max_s * 1000) + 1)       # no junction counting here
    end_since = None
    while True:
        ol, il, ir, orr = read()
        now = ticks_ms()
        if stop_at_edge and ol and orr and ticks_diff(now, f.t0) > QUIET_MS:
            stop()
            return "edge"
        if ol or il or ir or orr:
            end_since = None
        elif end_since is None:
            end_since = now
        elif ticks_diff(now, end_since) >= END_MS:
            stop()
            return "end of the line"
        if ticks_diff(now, f.t0) >= max_s * 1000:
            stop()
            return "time limit"
        f.update(ol, il, ir, orr)
        sleep_ms(1)


def advance(t_start):
    """Keep going until ADVANCE_MS after t_start (when the junction was first seen),
    so the wheels end up over the junction. Steers on the inner sensors only."""
    while ticks_diff(ticks_ms(), t_start) < ADVANCE_MS:
        il = inner_left.value()
        ir = inner_right.value()
        if il and not ir:
            drive(SLOW, FAST)
        elif ir and not il:
            drive(FAST, SLOW)
        else:
            drive(BASE, BASE)
        sleep_ms(1)
    stop()


def wait_for(test, t0, what):
    """Wait until test() is true twice in a row; stop and give up after TURN_MAX_MS."""
    n = 0
    while n < 2:
        n = n + 1 if test() else 0
        if ticks_diff(ticks_ms(), t0) > TURN_MAX_MS:
            stop()
            raise RuntimeError(what)
        sleep_ms(1)


def turn(direction):
    """Turn on the spot until both inner sensors are on a line again.

    direction: "left" / "right" = quarter turn, "round_left" / "round_right" = half turn.
    The first quarter turn is timed; after that, lines crossed in the first 60% of a
    quarter turn (or 75% of a half turn) are ignored, so the robot doesn't stop on a
    neighbouring rack line. That is also why RACK = 1 turns round clockwise: there is
    no rack line on that side of it.
    """
    global t90
    half = direction.startswith("round")
    clockwise = direction in ("right", "round_right")
    stop()
    sleep_ms(100)
    if clockwise:
        motorL.Forward(TURN)
        motorR.Reverse(TURN)
        trailing = inner_left        # the new line reaches the right sensor first
    else:
        motorL.Reverse(TURN)
        motorR.Forward(TURN)
        trailing = inner_right

    t0 = ticks_ms()
    blind = TURN_BLIND_MS
    if t90 is not None:
        blind = max(blind, int((1.5 if half else 0.6) * t90))
    while ticks_diff(ticks_ms(), t0) < blind:
        sleep_ms(1)
    wait_for(lambda: inner_left.value() == 0 and inner_right.value() == 0, t0,
             "turn " + direction + ": never got clear of the old line")
    wait_for(lambda: trailing.value() == 1, t0, "turn " + direction + ": line not found")
    stop()
    took = ticks_diff(ticks_ms(), t0)
    if not half and t90 is None:
        t90 = took
    say("  turned " + direction + " in " + str(took) + " ms")
    sleep_ms(100)


def pause(seconds):
    stop()
    sleep(seconds)


def route():
    """Start box -> rack line A<RACK>L -> Loading area <BAY> -> start box, left side.

    Start: in the start box on the long bottom line, facing LEFT, with the sensors
    between the centre line and the box's left edge.
    """
    t_begin = ticks_ms()

    say("1 bottom line to the corner, turn right")
    t = drive_to("right", 1, ignore_ms=int(START_IGNORE_S * 1000))
    leg1_ms = ticks_diff(t, t_begin)
    advance(t)
    turn("right")

    say("2 up the left line, turn right into rack line A" + str(RACK) + "L")
    t = drive_to("right", 2 + RACK)       # Loading area 2, Loading area 1, A1L, A2L...
    advance(t)
    turn("right")

    say("3 to the end of the rack line, stop, turn round")
    say("  stopped: " + drive_to_end(RACK_MAX_S, False))
    pause(PAUSE_S)
    turn("round_left" if RACK == 6 else "round_right")

    say("4 back to the left line, turn left")
    t = drive_to("both", 1)
    advance(t)
    turn("left")

    say("5 down the left line, turn left into Loading area " + str(BAY))
    t = drive_to("left", RACK - 1 + BAY)  # rack lines below, Loading area 1, Loading area 2
    advance(t)
    turn("left")

    say("6 to the loading area, stop, turn round")
    say("  stopped: " + drive_to_end(BAY_MAX_S, True))
    pause(PAUSE_S)
    turn("round_right")

    say("7 back to the left line, turn left, down to the corner, turn left")
    t = drive_to("both", 1)
    advance(t)
    turn("left")
    t = drive_to("left", 3 - BAY)         # (Loading area 2 if BAY is 1), then the corner
    advance(t)
    turn("left")

    say("8 along the bottom line into the start box")
    t = drive_to("left", 1, max_ms=int(leg1_ms * HOME_FACTOR))   # the centre line
    if t is None:
        say("  centre line not seen - stopped on time")
    else:
        drive_for(FINISH_EXTRA_S)
    stop()
    say("done")


def advance_test():
    """Tuning aid: drive to the next junction, on for ADVANCE_MS, then stop.
    The WHEELS should stop over the junction. Short of it: raise ADVANCE_MS.
    Past it: lower it."""
    t = drive_to("any", 1, ignore_ms=500)
    advance(t)
    stop()


def follow_forever():
    """Plain line following. Drives straight over every junction and says which kind it was."""
    f = Follower()
    n = 0
    while True:
        result = f.update(*read())
        if result:
            n += 1
            say("Junction " + str(n) + ": " + result[0])
        sleep_ms(1)


def check():
    """Wiring test: each wheel forward in turn, then live sensor readings."""
    print("WIRING CHECK - wheels off the table")
    sleep(2)

    print("LEFT wheel should now turn FORWARDS")
    motorL.Forward(40)
    sleep(1.5)
    motorL.off()
    sleep(1)

    print("RIGHT wheel should now turn FORWARDS")
    motorR.Forward(40)
    sleep(1.5)
    motorR.off()
    sleep(1)

    print("Sensors: centred on the line should read 0 1 1 0")
    print("OL IL IR OR   (outer left, inner left, inner right, outer right)")
    while True:
        print(outer_left.value(), "", inner_left.value(), "", inner_right.value(), "", outer_right.value())
        sleep(0.2)


if __name__ == "__main__":
    try:
        if MODE == "check":
            check()
        else:
            if START_DELAY_S:
                sleep(START_DELAY_S)
            if MODE == "route":
                route()
            elif MODE == "advance":
                advance_test()
            else:
                follow_forever()
    except RuntimeError as e:
        stop()
        say("STOPPED: " + str(e))
    finally:
        stop()