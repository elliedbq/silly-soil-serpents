# scan_i2c.py (MicroPython)
from machine import I2C, Pin
import time

# Pico W I2C0 on GP0 (SDA) / GP1 (SCL)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=50000)  # start slower for stability
time.sleep(0.2)
print([hex(x) for x in i2c.scan()])
