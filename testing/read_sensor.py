# read_sensor.py (MicroPython + driver port)
from machine import I2C, Pin
import time
from stemma_soil_sensor import StemmaSoilSensor

# Pico I2C0 pins (adjust if needed)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

ss = StemmaSoilSensor(i2c, addr=0x36)  # soil sensor at 0x36

while True:
    moisture = ss.get_moisture()
    temp = ss.get_temp()
    print("temp: {:.2f} °C  moisture: {}".format(temp, moisture))
    time.sleep(1)
