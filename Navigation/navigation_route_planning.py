#Route planning (for red and green boxes use magnets. blue boxes?)

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

