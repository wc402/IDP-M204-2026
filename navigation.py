#from time import ticks_diff, ticks_ms, sleep


class Navigation:
    def __init__(self):
        self.R1 = True
        self.R2 = True
        self.G1 = True
        self.G2 = True
        self.drop_area = [R1,R2,G1,G2]
        
    def set_angle(self, angle):

#word bank
#STRAIGHT, LEFT, RIGHT, SPIN, COLLECT, DROP, PARK, REVERSE, WAITING = range(9)

#reset at start of every Main sequence
N = 6
which_bay = 0
parcel_collected = False

#OVERARCHING SEQUENCE
Main_route = [Up_left, Up_right, Down_left, Down_right, Return]

#Major sequences
Up_left = [A_B, B_HL, HL_B, B_A, A_D, D_RG, RG_D, D_A]
Up_right = [A_B, B_HR, HR_B, B_A, A_D, D_RG, RG_D, D_A]
Down_left = [A_DL, DL_PL, PL_LL, LL_PL, PL_DL, DL_RG, RG_D, D_A]
Down_right = [A_DR, DR_PR, PR_LR, LR_PR, PR_DR, DR_RG, RG_D, D_A]
#must include turn at the end, in prep for next sequence
#D = DL or DR depending on polarity
#DL_RG and DR_RG is to R1,R2,G1,G2 depending on polarity and vacancy

#Minor sequences

#down_left
A_DL = [STRAIGHT, RIGHT]
DL_PL = [STRAIGHT, STRAIGHT]
PL_LL = [RIGHT, COLLECT, REVERSE, LEFT, CHECK_COLLECT] * N

def CHECK_COLLECT(which_bay, parcel_collected):
    which_bay += 1
    if parcel_collected = True:
        #FORCE MOVE ON TO LL_PL
        return which_bay

LL_PL = [REVERSE] * (which_bay+2)
PL_DL = [REVERSE, DECISION_L]

def DECISION_L:
    if package_polarity = 'red':
        pass
    elif package_polarity = 'green':
        additional_moves = [RIGHT, STRAIGHT, STRAIGHT, STRAIGHT, LEFT]
        for i in additional_moves:
            PL_DL.append(i)


#Return sequence

