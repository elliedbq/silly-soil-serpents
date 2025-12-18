import serial
import time
import math

# Serial connection
ser = serial.Serial('/dev/ttyACM1', 115200)

# ===== Common Parameters =====
num_servos = 6
calibration = [0, -20, 0, -30, 0, 0]
horizontal = [0, 1, 0, 1, 0, 1]

# ===== Serpentine Parameters =====
alpha = 100.0
omega = 2.0
K_n = 0.5
n = 3
beta = (2 * K_n * math.pi) / n

# ===== Control Flag =====
running = False


def serpentine_loop():
    global running
    start_time = time.perf_counter()

    while running:
        t = time.perf_counter() - start_time
        angles = []

        for j in range(num_servos):
            if horizontal[j] == 0:
                wave = alpha * math.sin(omega * t + j * beta)
                angle = round(wave, 0) + calibration[j]
            else:
                angle = calibration[j]

            servo_angle = max(0, min(180, angle + 90))
            angles.append(servo_angle)

        ser.write((",".join(map(str, angles)) + "\r\n").encode())
        time.sleep(0.05)


def sidewinding_loop():
    global running
    start_time = time.perf_counter()

    while running:
        t = time.perf_counter() - start_time

        s1 = 5 + 5 * math.sin(2 * math.pi * t)
        s2 = 22.5 + 22.5 * math.sin(2 * math.pi * t + math.pi / 2)
        s3 = 0
        s4 = 18 + 18 * math.sin(2 * math.pi * t + math.pi / 4)
        s5 = 5 + 5 * math.sin(2 * math.pi * t)

        angles = [max(0, min(180, round(a))) for a in [s1, s2, s3, s4, s5]]
        ser.write((",".join(map(str, angles)) + "\r\n").encode())
        time.sleep(0.05)
