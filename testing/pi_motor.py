import serial, time, math

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200)

calibration = [12, 12, 12, 12, 12, 12] #calibration for all motors
horizontal = [0, 1, 0, 1, 0, 1] #which motors move horizontally
num_servos = len(calibration)

# Definitions:
v_s = 0.5 #The snake's constant velocity along the curve (input, m/s)
n = 3 #number of links (3 links that can move horizontally)
L = 0.5 #total length, m
r = .06 #radius of curve, m
K_n = 0.5 #degree of curve
beta = (2*K_n*math.pi)/n #phase lag
# alpha_0 = curvature amplitude - don't know how to calculate??
joints = list((range(num_servos))) #joints that can move horizontally
t_run = 5 # run length (seconds)

# Parameters that we control:
alpha = 0.4 # winding angle parameter, change this to change the shape of the motion
omega = 0.5 # speed parameter, change this to change speed
gamma = -0.05 # heading parameter, changes direction (0=straight forward)

## Parameters in context:
# alpha = -2*alpha_0*sin(K*n*pi/n)
# omega = ((2*K*n*pi)/L)*v_s


## loop 1
start_time = time.perf_counter()
theta = list(range(len(joints)))

while True:
    current_time = time.perf_counter() - start_time
    for joint in joints:
        if horizontal[joint] == 1:
            angle = (alpha * math.sin(omega * current_time + joint * beta)) + calibration[joint]
            theta[joint] = round(angle, 3)

        else:
            theta[joint] = calibration[joint]
    # clamping
    theta[joint] = max(0, min(180, round(angle, 2)))

    # Servo target angles
    message = ",".join(map(str, theta)) + "\n"
    print(message)
    time.sleep(1)

    # # Send once
    # ser.write(message.encode('utf-8'))
    # time.sleep(1)
    # ser.close()