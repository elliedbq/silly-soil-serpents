from machine import Pin, PWM
import sys

# Setup 5 servos on GPIO pins
pins = [2, 4, 5, 6, 7, 9]
servos = [PWM(Pin(p)) for p in pins]
for s in servos:
    s.freq(50)  # Standard servo frequency

def angle_to_duty(angle):
    # Map 0–180° to duty cycle (adjust for your servos)
    # clamp angle (avoid damage to servo)
    angle = max(0, min(180, angle))
    # servo specific range (min = 0, max = 180)
    mini_range = 1000
    max_range = 2000
    # convert angle to pulse width
    p_width = mini_range + (max_range - mini_range) * angle/180
    # convert pulse width to duty_u16
    duty = int(p_width * 65535/20000)
    return duty

while True:
    line = input() #sys.stdin.readline()  # Read from USB serial
    print("Raw:", repr(line))
    if not line:
        continue
    try:
        tokens = line.strip().split(",")
        #angles = [float(x) for x in line.strip().split(",")] # may change to int
        angles = []
        for x in tokens:
            if x:  # skip empty strings
                angles.append(float(x))
        for servo, angle in zip(servos, angles):
            duty = angle_to_duty(angle)
            print("Angle:", angle, "Duty:", duty)
            servo.duty_u16(duty)
            #servo.duty_u16(angle_to_duty(angle))
    except Exception as e:
        print("Parse error:", e, line)