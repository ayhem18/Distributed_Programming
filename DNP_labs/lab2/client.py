import socket

server_address = ('127.0.0.1', 1234)
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print("Welcome to the calculator client.\n\n")
while True:
    try:
        cmd = input("Enter the calculation that you want to perform: ")
        if cmd == 'QUIT':
            break
        sock.sendto(cmd.encode('utf-8'), server_address)

        msg, address = sock.recvfrom(1024)
        print(f"RESULT: {msg.decode('utf-8')}")
    except KeyboardInterrupt:
        break

sock.close()
print('Client shutting down.')


