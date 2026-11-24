#navigation programs

#class Navigation:
#    def


#word bank
#STRAIGHT, LEFT, RIGHT, SPIN, COLLECT, DROP, PARK, REVERSE, WAITING = range(9)


DROP_AREA = [R1,R2,G1,G2] #True if empty
R1,R2,R3,R4 = True, True, True, True

#reset at start of every Main sequence
N = 6
which_bay = 0
parcel_collected = False

#OVERARCHING SEQUENCE
Route = [Up_left, Up_right, Down_left, Down_right, Return]

#Main sequences
Up_left = [A_B, B_HL, HL_B, B_A, A_D, D_RG, RG_D, D_A]
Up_right = [A_B, B_HR, HR_B, B_A, A_D, D_RG, RG_D, D_A]
Down_left = [A_DL, DL_PL, PL_LL, LL_PL, PL_DL, DL_RG, RG_D, D_A]
Down_right = [A_DR, DR_PR, PR_LR, LR_PR, PR_DR, DR_RG, RG_D, D_A]
#must include turn at the end, in prep for next sequence
#D = DL or DR depending on polarity
#DL_RG and DR_RG is to R1,R2,G1,G2 depending on polarity and vacancy

#Individual paths
#down_left
A_DL = [STRAIGHT, RIGHT]
DL_PL = [STRAIGHT, STRAIGHT]
PL_LL = [RIGHT, COLLECT, REVERSE, LEFT, CHECK_COLLECT] * N

def CHECK_COLLECT(which_bay, parcel_collected):
    which_bay += 1
    if parcel_collected = True:
        
    

#for each iteration, which_bay +=1
#set package_polarity to 'red' or 'green'
#break from PL_LL when parcel_collected = True
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





#0: straight ahead
#1: turn left
#2: turn right
#3: stop for pickup #time of flight rather than line sensor, follow with 4 (prompt a change detection)
#4: reverse (meaning backup till detect another change)
#5: stop for dropping parcel, then follow with 4 (prompt a change detection)

#Every time detects and verifies change
#split into segments for us to keep track when coding
#replace variable 'route' with appropriate list

left_bay = [1,0,2,0,0]
left_pickup = [2,3,4,1] * 6
#keep count of no.left_pickup iterations so we know what bay the parcel was picked up from
#if detects parcel, break route

left_return = [4,4,4,4,4,4,4] #def one 4, then number of 4s depends on what bay they stopped at

#case red parcel
left_red_dropoff_1 = [2,5,4,2,0,1,0,1]
# if first red occupied, break left_red_dropoff_1 before 5
left_red_dropoff_2 = [4,2,1,5,4,2,1,0,1]

#case blue parcel
left_blue_dropoff_1 = [0,0,1,0,0,0,1,1,5,4,1,2,0,2]
#if first blue occupied, break left_blue_dropoff_1 before 5
left_blue_dropoff_2 = [4,2,1,5,4,1,0,2,0,2]

#case no parcel, has reached t junction
#if doesn't detect parcel at all, need to check again
left_check_again = [4,4,4,4,4,4]
#repeat from left_pickup
#if no parcel again
left_cut_losses = [4,4,4,4,4,4,4,4,4,2,0,1] #ensure transition from 4->2 works



right_bay = [2,0,1,0,0]
right_pickup = [1,3,4,1] * 6
right_return = [4,0,0,0,0,0,0]


