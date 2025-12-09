from machine import I2C, Pin
import time
import sys

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
SENSOR_ADDR = 0x36

def read_moisture():
    try:
        data = i2c.readfrom_mem(SENSOR_ADDR, 0x0F, 2)
        return (data[0] << 8) | data[1]
    except OSError as e:
        print("I/O error, retrying:", e)
        return None


def read_temperature():
    try:
        data = i2c.readfrom_mem(SENSOR_ADDR, 0x10, 2)
        raw = (data[0] << 8) | data[1]
        return raw / 10.0
    except OSError as e:
            print("I/O error, retrying:", e)
            return None

while True:
    moisture = read_moisture()
    temp = read_temperature()

    # Send CSV-style line over USB serial
    print(f"{moisture},{temp}")


    time.sleep(1)