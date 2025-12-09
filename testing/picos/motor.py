import machine
import time

# Define the GPIO pin connected to the servo's signal wire
servo_pin = machine.Pin(28) # Example: GPIO16

# Create a PWM object on that pin
servo = machine.PWM(servo_pin)

# Set the PWM frequency to 50 Hz (standard for servos)
servo.freq(50)

# --- Helper Function to Set Angle ---
# Maps 0-180 degrees to the 16-bit duty cycle (0-65535)
def set_angle(angle):
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
