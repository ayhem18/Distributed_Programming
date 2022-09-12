import socket
import sys
import random
from threading import Thread, Lock

server_ip = '127.0.0.1'
server_port = None
try:
    server_port = int(sys.argv[1])
except:
    print("No port was defined for the server.")
    print("Usage example: python3 ./server.py <port>")
    exit(0)

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
try:
    sock.bind((server_ip, server_port))
except Exception as e:
    print('Error while binding to the specified port.')
    exit(0)

sock.listen()
print(f"Starting the server on {server_ip}:{server_port}")

port_increment = 1
port_increment_lock = Lock()


# function for the thread game
def game(conn: socket.socket, addr):
    try:
        global port_increment
        while True:
            port_increment_lock.acquire()
            port_increment += 1
            new_port = server_port + port_increment
            port_increment_lock.release()
            sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            try:
                sock.bind((server_ip, new_port))
                break
            except Exception as e:
                print(f"Error when binding thread socket : {e}\nTrying a new port.")
        conn.sendall(str(new_port).encode())
        conn.close()
        sock.listen()
        sock.settimeout(5)  # set the timeout for connecting to the client
        try:
            conn, addr = sock.accept()
            sock.settimeout(None)
        except socket.timeout:
            sock.close()
            return

        conn.sendall("Welcome to the number guessing game! Enter the range :".encode())
        msg = conn.recv(1024).decode()
        while True:
            try:
                msg = msg.split()
                lo = int(msg[0])
                hi = int(msg[1])
                assert len(msg) == 2
                break
            except:
                # print(e)
                conn.sendall(
                    "Enter the range:".encode())
                msg = conn.recv(1024).decode()
                continue

        x = random.randint(lo, hi)
        attempts = 5
        conn.sendall(f"You have {attempts} attempts left.".encode())
        while True:
            msg = conn.recv(1024).decode()
            try:
                msg = int(msg)
                assert lo <= msg <= hi
            except Exception as e:
                print(e)
                conn.sendall(
                    "Invalid input. Please make sure you enter one integer within the chosen range. You may try again.".encode())
                continue
            attempts -= 1
            if msg == x:
                conn.sendall("You win!".encode())
                conn.close()
                return
            if attempts == 0:
                conn.sendall("You lose!".encode())
                conn.close()
                return
            response = ("Less", "Greater")[msg < x]
            conn.sendall(f"{response}\nYou have {attempts} attempts.".encode())
    except:
        return


threads = []

while True:
    try:
        print("Waiting for a connection")
        conn, address = sock.accept()

        # remove terminated threads from the list
        threads = [t for t in threads if t.is_alive()]
        if len(threads) == 2:
            conn.sendall("The server is full".encode())
            conn.close()
            continue

        print("Connection established with the client.")
        t = Thread(target=game, args=(conn, address,), daemon=True)
        threads.append(t)
        t.start()
    except KeyboardInterrupt:
        print("Server received a KeyboardInterrupt.")
        print("Shutting down the server ...")
        sock.close()
        exit(0)
