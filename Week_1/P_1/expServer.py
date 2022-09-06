import socket as sk

serverPort = 12000

serverSocket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

serverSocket.bind(("127.0.0.1", serverPort))

while 1:

    message, clientAddress = serverSocket.recvfrom(2048)

    print(clientAddress)

    modifiedMessage = message.upper()

    serverSocket.sendto(modifiedMessage, clientAddress)