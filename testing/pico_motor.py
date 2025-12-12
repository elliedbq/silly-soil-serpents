from machine import Pin, PWM
import sys

# Setup 5 servos on GPIO pins
pins = [28, 3, 4, 5, 6]
servos = [PWM(Pin(p)) for p in pins]
for s in servos:
    s.freq(50)  # Standard servo frequency

def angle_to_duty(angle):
    # Map 0–180° to duty cycle (adjust for your servos)
    # clamp angle (avoid damage to servo)
    angle = max(0, min(180, angle))
    # servo specific range (min = 0, max = 180)
    mini_range = 800
    max_range = 2200
    # convert angle to pulse width
    p_width = mini_range + (max_range - mini_range) * angle/180
    # convert pulse width to duty_u16
    duty = int(p_width * 65535/20000)
    return duty

while True:
    line = sys.stdin.readline()  # Read from USB serial
    if not line:
        continue
    try:
        angles = [int(x) for x in line.strip().split(",")]
        for servo, angle in zip(servos, angles):
            servo.duty_u16(angle_to_duty(angle))
    except:
        pass