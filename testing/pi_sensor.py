import serial
import csv
from datetime import datetime

ser = serial.Serial('/dev/ttyACM1', 115200)

csv_file = "soil_data.csv"

# Create file with header if needed
try:
    open(csv_file, "x").write("timestamp,moisture,temperature\n")
except FileExistsError:
    pass

while True:
    line = ser.readline().decode().strip()
    if not line:
        print("No data received, retrying...")
        continue
    try:
        moisture, temp = line.split(",")
    except ValueError:
        print("Malformed line:", line)
        continue

    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), moisture, temp])

    print("Logged:", moisture, temp)