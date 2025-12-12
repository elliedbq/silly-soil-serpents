# code to calculate servo angles for sidewinding motion

import serial, time, math

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200)

calibration = [12, 12, 12, 12, 12, 12] #calibration for all motors
horizontal = [0, 1, 0, 1, 0, 1] #which motors move horizontally
num_servos = len(calibration)
# initialize list of servo angles
theta = [0] * num_servos # will be sent to the pico

# convert radians to degrees
def radians_to_degrees(rad):
    return rad *180/math.pi

# correct offset and clamp
def apply_calibration(angle_deg, servo_index):
    corrected = angle_deg + calibration[servo_index]
    return max(0, min(180, round(corrected, 2)))

# loop to calculate servos angles for sidewinding motion
# servos 3 and 5 will be at a constant 90 degrees throughout
# the entire run

while True:
    forward_positions = [i * 0.01 for i in range(int(0.174 / 0.01) + 1)]
    for pos in forward_positions:
        theta[0] = apply_calibration(radians_to_degrees(pos),0)
        
'''
# Definitions
L = 0.11; # Link length estimate meters
# First Positions
pt1 = [0,0]
pt2 = [2*L*math.sin(-5*math.pi/4), 2*L*math.cos(-5*math.pi/4)]
pt3 = [pt2(1) + 2*L*math.sin(-7*math.pi/4), pt2(2) + 2*L*math.cos(-7*math.pi/4)]
pt4 = [pt3(1) + 2*L*math.sin(-5*math.pi/4), pt3(2) + 2*L*math.cos(-5*math.pi/4)]
pts = [pt1; pt2; pt3; pt4]

# Second Positions
pt4_2 = pt4
pt3_2 = pt3
pt2_2 = [pt3_2(1)-2*L, pt3_2(2)]
pt1_2 = [0, pt2_2(2) + 2*L*math.cos(pi/4)]
pts_2 = [pt1_2; pt2_2; pt3_2; pt4_2]

## Back to Original Shape
pts_3 = [pts(:,1), pts(:,2)+(pt3_2(2) - pt4_2(2))]
'''

