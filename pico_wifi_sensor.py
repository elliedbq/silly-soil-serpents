from machine import Pin, PWM
import sys
import network
import socket
from time import sleep
from picozero import pico_led
import machine
import rp2

# wifi credentials
ssid = 'OLIN-DEVICES'
password = 'BestOval4Engineers!'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 8080)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def angle_to_duty(angle):
    # Map 0–180° to duty cycle (adjust for your servos)
    # clamp angle (avoid damage to servo)
    #angle = max(0, min(180, angle))
    # servo specific range (min = 0, max = 180)
    mini_range = 1000
    max_range = 2600
    # convert angle to pulse width
    p_width = mini_range + (max_range - mini_range) * angle/180
    # convert pulse width to duty_u16
    duty = int(p_width * 65535/20000)
    return duty


ip = connect()
print(ip)
connection = open_socket(ip)

# Setup 5 servos on GPIO pins
motor_pin = 27
servo = PWM(Pin(motor_pin))
servo.freq(50)  # Standard servo frequency

client, addr = connection.accept()
print('Client connected from', addr)

buffer = b""

while True:
    data = client.recv(32)
    if not data:
        break

    buffer += data
    try:
        if b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            angle = float(line.decode().strip())

            duty = angle_to_duty(angle)
            servo.duty_u16(duty)

    except Exception as e:
            print("Parse error:", e, line)

client.close()
print("Socket closed")