from machine import Pin, PWM
import sys

# Setup 5 servos on GPIO pins
pins = [28, 3, 4, 5, 6]
servos = [PWM(Pin(p)) for p in pins]
for s in servos:
    s.freq(50)  # Standard servo frequency

def angle_to_duty(angle):
    # Map 0–180° to duty cycle (adjust for your servos)
    return int(1638 + (angle/180)*6553)  # 0.5–2.5 ms pulse

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