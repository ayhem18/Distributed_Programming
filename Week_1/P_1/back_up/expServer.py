import socket as sk

serverPort = 12000

serverSocket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)

serverSocket.bind(("127.0.0.1", serverPort))

while 1:

    message, clientAddress = serverSocket.recvfrom(10000)
    i = 0
    with open("server.png", 'ab') as f:
        f.write(message)
        i += 1
    print("just wrote chunk of data")
