import socket as sk
import sys
import re
from multiprocessing import Queue
from queue import Empty
from copy import copy

ip = '127.0.0.1'
TIME_OUT = 30  # 10 seconds of inactivity before shutting down
BUFFER_SIZE = 4096


def put_command(q: list, data: str):
    print(data)
    comps = re.split(r'(\s)+', data)
    print(comps)
    q.append(comps[2])
    return f"{comps[2]} was added to the queue"


def pick_command(q: list, data: str):
    if q:
        return q[0]
    else:
        return None


def pop_command(q: list, data: str):
    if q:
        head = q[0]
        q.remove(head)
        return head
    else:
        return None


def size_command(q: list, data: str):
    return len(q)


def serve_client(q: list, data: bytes):
    data_str = data.decode().strip().lower()
    put_pattern = r'put(\s)+(\S)+'
    if re.match(put_pattern, data_str) is not None:
        return put_command(q, data_str)
    elif data_str == 'size':
        return size_command(q, data_str)
    elif data_str == 'pick':
        return pick_command(q, data_str)
    else:
        return pop_command(q, data_str)


def server(port: int):
    clients_queue = []  # an infinite queue

    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as s:
        s.bind((ip, port))
        s.settimeout(TIME_OUT)  # this will make the
        while True:
            try:
                data, addr = s.recvfrom(BUFFER_SIZE)
                reply = str(serve_client(clients_queue, data))
                s.sendto(reply.encode(), addr)
            except sk.timeout:
                print(f"INACTIVE FOR {str(TIME_OUT)} seconds ... SHUTTING DOWN")
                sys.exit()
            except KeyboardInterrupt:
                print("Server Shutting down...")
                sys.exit()


def main():
    args = sys.argv
    if len(args) == 2:  # make sure the port number is passed
        server(int(args[1]))
    else:
        server(5000)


if __name__ == "__main__":
    main()
