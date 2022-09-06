import socket as sk
import sys

serverName = "127.0.0.1"

serverPort = 12000

try:
    clientSocket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
except sk.error:
    sys.exit()

message = "MESSAGE WHATEVER".encode()

ser_addr = (serverName, serverPort)

clientSocket.sendto(message, ser_addr)

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

clientSocket.sendto(message, ser_addr)

clientSocket.close()
