import socket
import serial, time, math

calibration = [0, -20, 0, -30, 0, 0] #calibration for all motors
horizontal = [0, 1, 0, 1, 0, 1] #which motors move horizontally
num_servos = len(calibration)

# Definitions:                                                                                                                                                                               
v_s = 0.5 #The snake's constant velocity along the curve (input, m/s)
n = 3 #number of links (3 links that can move horizontally)
L = 0.126 #total length, m
r = 0.095 #radius of curve, m
K_n = 0.5 #degree of curve
beta = (2*K_n*math.pi)/n #phase lag
# alpha_0 = curvature amplitude - don't know how to calculate??
joints = list((range(num_servos))) #joints that can move horizontally
t_run = 10 # run length (seconds)

# Parameters that we control:z
alpha = 90.0 # winding angle parameter, change this to change the shape of the motion
omega = 2.0 # speed parameter, change this to change speed
gamma = -0.05 # heading parameter, changes direction (0=straight forward)

## Parameters in context:
# alpha = -2*alpha_0*sin(K*n*pi/n)
# omega = ((2*K*n*pi)/L)*v_s


start_time = time.perf_counter()
theta = [0.0] * num_servos

HOST =  '192.168.34.119'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        current_time = time.perf_counter() - start_time
        for joint in joints:
            if horizontal[joint] == 0:
                wave = (alpha * math.sin(omega * current_time + joint * beta))
                angle = round(wave, 0) + calibration[joint]
            else:
                angle= calibration[joint]
            # clamping
            servo_angle = angle + 90
            theta[joint] = max(0, min(180, servo_angle))

            #theta[joint] = max((calibration[joint]-90), min((calibration[joint]+90), round(angle, 0)))

        # Servo target angles
        message = ",".join(map(str, theta)) + "\r\n"
        s.sendall(message.encode())
        print("sent:",message)
        time.sleep(0.05)
