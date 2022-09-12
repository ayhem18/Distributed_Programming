import threading
from multiprocessing import Queue
from queue import Empty  # exception to break from loop when the get(block=False) called on empty queue
from threading import Thread

import checking as ck
import socket as sk

PORT = 8888
IP_ADDRESS = '127.0.0.1'
SERVER_BUFF_SIZE = 2048

SERVER_REPLY_TRUE = "TRUE"
SERVER_REPLY_FALSE = "FALSE"
NUM_THREADS = 5
SERVER_SHUT_DOWN = "SERVER SHUTTING DOWN"
MAX_WORKERS = 50


def display_working_thread(client_addr):
    print("{t_name} is serving the client with address {c_addr}".
          format(t_name=threading.current_thread().name, c_addr=client_addr))


def serve_client(client_info: tuple):
    client_conn = client_info[0]
    client_addr = client_info[1]
    display_working_thread(client_addr)
    try:
        while True:
            num = int(client_conn.receive(SERVER_BUFF_SIZE).decode())
            reply_data = (SERVER_REPLY_TRUE if ck.is_prime(num) else SERVER_REPLY_FALSE).encode()
            client_conn.sendall(reply_data)
    except KeyboardInterrupt:
        client_conn.close()
        print(SERVER_SHUT_DOWN)
        return
    except:
        client_conn.close()
        return


def do_jobs(queue: Queue, workers: list):
    try:
        print("entering to fetch one client's info!!")
        c_info = queue.get(block=False)
        print("create thread to server client " + str(c_info[1]))
        new_thread = Thread(target=serve_client, args=(c_info,))
        workers.append(new_thread)
        new_thread.start()
        new_thread.join()
    except Empty:
        print("The queue is empty for some reason")
        return


def server(port: int):
    jobs_queue = Queue(maxsize=MAX_WORKERS)
    workers = []

    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as s:
        try:
            s.bind((IP_ADDRESS, port))
            while True:
                # listening for the connections
                s.listen()
                conn, addr = s.accept()
                print("adding connection " + str(addr) + " to the queue")
                jobs_queue.put((conn, addr), block=False)  # adding the client's info to the queue
                do_jobs(jobs_queue, workers)
        except KeyboardInterrupt:
            s.close()  # close the main socket
            exit()
        except (PermissionError, OSError, OverflowError):
            print('Error when binding to the specified port')
            exit()


if __name__ == "__main__":
    server(PORT)
