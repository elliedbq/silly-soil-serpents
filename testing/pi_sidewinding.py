import serial, time, math

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200)

# Calibration offsets for each servo
calibration = [0, -20, 0, -30, 0, 0]  # calibration for all motors
horizontal = [0, 1, 0, 1, 0, 1]  # which motors move horizontally    
num_servos = len(calibration)

# Definitions
v_s = 0.5 #The snake's constant velocity along the curve (input, m/s)
n = 3 #number of links (3 links that can move horizontally)
L = 0.126 #total length, m
r = 0.095 #radius of curve, m
K_n = 0.5 #degree of curve
beta = (2*K_n*math.pi)/n #phase lag
# alpha_0 = curvature amplitude - don't know how to calculate??
joints = list((range(num_servos))) #joints that can move horizontally
t_run = 10 # run length (seconds)

# Parameters we control
alpha = 90.0 # winding angle parameter, change this to change the shape of the motion
omega = 2.0 # speed parameter, change this to change speed
gamma = -0.05 # heading parameter, changes direction (0=straight forward)

# Sidewinding specific parameters 
alpha_side = 45.0   # smaller amplitude for sidewinding
omega_side = 1.5    # slower frequency
phase_offset = math.pi / 4 

# Continuous loop
start_time = time.perf_counter()
theta = [0.0] * num_servos

while True:
    current_time = time.perf_counter() - start_time
    for joint in joints:
        if horizontal[joint] == 0:
            # Vertical joints: small oscillation
            wave = alpha_side * math.sin(omega_side * current_time + joint * beta)
            angle = round(wave, 0) + calibration[joint]
        else:
            # Horizontal joints: shifted sine wave
            wave = alpha_side * math.sin(omega_side * current_time + joint * beta + phase_offset)
            angle = round(wave, 0) + calibration[joint]

        # Clamp to servo range
        servo_angle = angle + 90
        theta[joint] = max(0, min(180, servo_angle))

    # Servo target angles
    message = ",".join(map(str, theta)) + "\r\n"
    ser.write(message.encode("utf-8"))
    print(message)
    time.sleep(0.05)
