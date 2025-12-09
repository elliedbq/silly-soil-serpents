import serial, time

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200)

# Servo target angles
angles = [90, 45, 120, 60, 30]
message = ",".join(map(str, angles)) + "\n"

# Send once
ser.write(message.encode('utf-8'))
time.sleep(1)
ser.close()