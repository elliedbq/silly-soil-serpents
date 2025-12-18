# example

import socket, time

HOST =  '192.168.35.242'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    while True:
        data = s.recv(1024)
        if not data:
            break   # Pico closed connection

        print("Received:", data.decode())
        s.sendall(b'ACK\n')
