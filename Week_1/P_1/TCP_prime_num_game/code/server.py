import socket as sk
import sys
import threading
from multiprocessing import Queue
from threading import Thread

import checking as ck

PORT = 8888
IP_ADDRESS = '127.0.0.1'
SERVER_BUFF_SIZE = 2048

SERVER_REPLY_TRUE = "TRUE"
SERVER_REPLY_FALSE = "FALSE"
NUM_THREADS = 5
SERVER_SHUT_DOWN = "SERVER SHUTTING DOWN"
MAX_CLIENTS = 50
WORKERS = 5
TIMEOUT = 1

def display_working_thread(client_addr):
    print("{t_name} is serving the client with address {c_addr}".
          format(t_name=threading.current_thread().name, c_addr=client_addr))


def display_thread_terminating():
    print("{t_name} is terminating as the server is down".format(t_name=threading.current_thread().name))


def thread_function(jobs_queue: Queue):
    try:
        while True:  # this means the program will keep
            client_info = jobs_queue.get()
            # the None value is an indicator that the thread must terminate
            if client_info is None:
                sys.exit()

            client_conn = client_info[0]
            client_addr = client_info[1]
            display_working_thread(client_addr)
            try:
                while True:
                    num = int(client_conn.recv(SERVER_BUFF_SIZE).decode())
                    reply_data = (SERVER_REPLY_TRUE if ck.is_prime(num) else SERVER_REPLY_FALSE).encode()
                    client_conn.sendall(reply_data)
            except:
                print("client with address {addr} terminated its session".format(addr=client_addr))
    except:
        print(display_thread_terminating())


def server(port: int):
    print("SERVER STARTING")
    jobs_queue = Queue(maxsize=MAX_CLIENTS)
    workers = [Thread(target=thread_function, args=(jobs_queue,)) for _ in range(WORKERS)]
    for t in workers:
        t.start()

    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as s:
        try:
            s.bind((IP_ADDRESS, port))
            while True:
                # listening for the connections
                s.listen()
                conn, addr = s.accept()

                print("adding connection " + str(addr) + " to the queue")
                jobs_queue.put((conn, addr))  # adding the client's info to the queue
        except KeyboardInterrupt:
            print("SERVER SHUTTING DOWN")
            # making the main thread wait for the workers

            for _ in workers:  # adding None values in the queue as a signal for the thread to terminate
                jobs_queue.put(None)  # putting None for each thread causing them to terminate

            for t in workers:
                t.join()

            s.close()  # close the main socket
            sys.exit()
        except (PermissionError, OSError, OverflowError):
            print('Error when binding to the specified port')
            for t in workers:
                t.join()
            sys.exit()


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        p = int(args[1])
        server(p)
    else:
        server(PORT)
