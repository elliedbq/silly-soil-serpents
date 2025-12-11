'''from machine import I2C, Pin
import time
import sys

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
SENSOR_ADDR = 0x36

def read_moisture():
    i2c.writeto_mem(SENSOR_ADDR,0x0A, b'\x0F')  # trigger measurement
    time.sleep(1.0)  # give sensor time to measure
    data = i2c.readfrom_mem(SENSOR_ADDR, 0x00, 2)
    return (data[0] << 8) | data[1]

def read_temperature():
    data = i2c.readfrom_mem(SENSOR_ADDR, 0x05, 2)
    raw = (data[0] << 8) | data[1]
    return raw / 10.0


while True:
    moisture = read_moisture()
    temp = read_temperature()

    # Send CSV-style line over USB serial
    print(f"{moisture},{temp}")


    time.sleep(1)'''

from machine import I2C, Pin

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
SENSOR_ADDR = 0x36

try:
    data = i2c.readfrom_mem(SENSOR_ADDR, 0x0D, 2)
    version = (data[0] << 8) | data[1]
    print("Firmware version register:", version, "raw:", data)
except OSError as e:
    print("I/O error:", e)
