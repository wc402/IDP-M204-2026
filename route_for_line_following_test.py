#line following test route

left_bay = [1,0,2,0,0]
left_pickup = [2,3,4,1] * 6
#keep count of no.left_pickup iterations so we know what bay the parcel was picked up from
#if detects parcel, break route

left_return = [4,4,4,4,4,4,4] #def one 4, then number of 4s depends on what bay they stopped at

#case red parcel
left_red_dropoff_1 = [2,5,4,2,0,1,0,1]


#start
route = left_bay
for i in route:
    
    if i == 0:
        #straight ahead
    elif i == 1:
        #turn left
    elif i == 2:
        #turn right
    elif i == 3:
        #pause to pickup
        #trigger a change detection
    elif i == 4:
        #back up
    elif i == 5:
        #pause to drop
    else:
        #error
    