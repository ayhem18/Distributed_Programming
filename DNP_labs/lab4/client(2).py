import sys
import socket
import time

try:
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
except Exception as e:
    print(e)
    print("Invalid server and port arguments.\nUsage example: python ./client.py <address> <port>")
    exit(0)

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
try:
    sock.connect((server_ip, server_port))
except ConnectionError:
    print("Server is unavailable.")
    exit(0)

init = False

while True:
    try:
        msg = sock.recv(1024).decode()

        if not init:
            if msg == "The server is full":
                print(msg)
                exit(0)
            new_port = int(msg)
            sock.close()
            sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            time.sleep(1)
            try:
                sock.connect((server_ip, int(msg)))
            except ConnectionRefusedError:
                print("Connection refused. (Might be because of a timeout).")
                exit(0)
            init = True
            continue
        print(msg)
        if msg in ["You win!", "You lose!"] or "ERROR" in msg:
            sock.close()
            exit(0)
        response = input("> ")
        sock.send(response.encode())
    except KeyboardInterrupt:
        print("Exiting client ...")
        sock.close()
        exit(0)
    except ConnectionError:
        print("Connection with server lost. Exiting ...")
        sock.close()
        exit(0)
