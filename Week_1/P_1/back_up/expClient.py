import socket as sk
import sys
import os
import time

serverName = "127.0.0.1"

serverPort = 12000

try:
    clientSocket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
except sk.error:
    sys.exit()


ser_addr = (serverName, serverPort)

image = os.path.join("test_files/test.png")

b_size = 10000
i = 0
f_s = os.path.getsize(image)

with open(image, 'rb') as f:
    next_i = min(i + b_size, f_s)
    while i < f_s:
        message = f.read()[i: next_i]
        clientSocket.sendto(message, ser_addr)
        i = next_i
        time.sleep(0.5)

clientSocket.close()
