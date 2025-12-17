import serial
import time
import math
import socket

# wifi connection
HOST_motor =  '192.168.34.119'
HOST_sensor = '192.168.35.242'
PORT = 8080

# ===== Common Parameters =====
num_servos = 6
calibration = [0, -20, 0, -30, 0, 0]
horizontal = [0, 1, 0, 1, 0, 1]

# ===== Serpentine Parameters =====
alpha = 60.0
omega = 2.0
K_n = 0.5
n = 3
beta = (2 * K_n * math.pi) / n

# ===== Control Flag =====
running = False


def socket_sender_loop(angle_generator):
    """
    Generic loop that sends servo angles over TCP
    angle_generator() must return a list of angles
    """
    global running

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST_motor, PORT))
        start_time = time.perf_counter()

        while running:
            angles = angle_generator(start_time)
            message = ",".join(map(str, angles)) + "\r\n"
            s.sendall(message.encode())
            print("sent:", message)
            time.sleep(0.05)


def serpentine_angles(start_time):
    t = time.perf_counter() - start_time
    theta = [0] * num_servos

    for joint in range(num_servos):
        if horizontal[joint] == 0:
            wave = alpha * math.sin(omega * t + joint * beta)
            angle = round(wave, 0) + calibration[joint]
        else:
            angle = calibration[joint]

        servo_angle = angle + 90
        theta[joint] = max(0, min(180, servo_angle))

    return theta


def serpentine_loop():
    socket_sender_loop(serpentine_angles)



def sidewinding_angles(start_time):
    t = time.perf_counter() - start_time

    s1 = 5 + 5 * math.sin(2 * math.pi * t)
    s2 = 22.5 + 22.5 * math.sin(2 * math.pi * t + math.pi / 2)
    s3 = 0
    s4 = 18 + 18 * math.sin(2 * math.pi * t + math.pi / 4)
    s5 = 5 + 5 * math.sin(2 * math.pi * t)

    return [max(0, min(180, round(a))) for a in [s1, s2, s3, s4, s5]]


def sidewinding_loop():
    socket_sender_loop(sidewinding_angles)


def lower_sensor():
    socket_to_motor(20)

def raise_sensor():
    socket_to_motor(40)

def socket_to_motor(angle):
    """
    Generic loop that sends servo angles over TCP
    angle_generator() must return a list of angles
    """
    global running

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST_sensor, PORT))

        message = str(angle) + "\r\n"
        s.sendall(message.encode())
        print("sent to sensor:", message)
        time.sleep(0.05)    
