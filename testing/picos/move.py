import machine
import time

# define GPIO pins
pin1 = machine.Pin(2, machine.Pin.OUT)  

# create a PWM object on a pin
servo1 = machine.PWM(pin1)

# set PWM frequency to 50Hz for servos
servo1.freq(50)

# --- Helper Function to Set Angle ---
# Maps 0-180 degrees to the 16-bit duty cycle (0-65535)
def set_angle(angle, servo):
    # Standard SG90 servo range: ~1350 (0 deg) to ~8200 (180 deg) for 50Hz
    # duty_u16 uses values 0-65535; adjust these values for your servo
    duty = int(1350 + (angle / 180) * (8200 - 1350))
    print(duty)
    servo.duty_u16(duty)


# --- Main Loop ---
try:
    print("Moving servo to 0 degrees...")
    set_angle(0)
    time.sleep(1)

    print("Moving servo to 90 degrees...")
    set_angle(90)
    time.sleep(1)

    print("Moving servo to 180 degrees...")
    set_angle(180)
    time.sleep(1)

    print("Moving servo to 270 degrees...")
    set_angle(240)
    time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user.")
    servo.deinit() # Stop PWM
