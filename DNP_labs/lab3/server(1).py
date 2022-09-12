import socket
import time
import os
from datetime import datetime
from threading import Thread, Lock

server_address = ('127.0.0.1', 1234)
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(server_address)
sock.setblocking(False)
sock.settimeout(1500)

sessions = {}
sessions_lock = Lock()

buff_size = 2048
file_directory = './server_data'

if not os.path.exists(file_directory):
    os.makedirs(file_directory)


def session_manager():
    global sessions
    global sessions_lock
    while True:
        sessions_lock.acquire()
        to_remove = []
        for i in sessions:
            # print(i)
            # print((datetime.now() - sessions[i]['last_packet']).total_seconds())
            if sessions[i]['finished'] and (datetime.now() - sessions[i]['last_packet']).total_seconds() > 1:
                to_remove.append(i)
                continue
            if (datetime.now() - sessions[i]['last_packet']).total_seconds() > 3:
                to_remove.append(i)
                continue
        for i in to_remove:
            sessions.pop(i, None)
            print(f"Session for {i} cleared.")

        # print(sessions)
        sessions_lock.release()
        time.sleep(0.2)


p = Thread(target=session_manager)
p.start()
while True:
    # print(sessions)
    msg, address = sock.recvfrom(buff_size + 16)  # 16 bytes are reserved for the metadata
    # print(msg)
    sessions_lock.acquire()
    if sessions.get(address) is None:
        packet, seq, extension, size = msg.decode('utf-8').split('|', 3)
        if packet != 's':
            continue
        print(f"Started file transfer from {address}")
        entry = {
            'seq': int(seq),
            'extension': extension,
            'size': int(size),
            'filename': f"{address}_{time.time()}",
            'received': b"",
            'finished': False,
            'last_packet': datetime.now()
        }
        sessions[address] = entry
        sessions[address]['seq'] += 1
        sock.sendto(f"a|{sessions[address]['seq']}|{buff_size}".encode('utf-8'), address)

    else:
        d, seq, data = msg.split(b"|", 2)
        sessions[address]['last_packet'] = datetime.now()
        seq = int(seq.decode('utf-8'))
        # print(data)
        # discard duplicate
        if seq < sessions[address]['seq']:
            continue

        sessions[address]['received'] += data
        sessions[address]['seq'] += 1
        sock.sendto(f"a|{sessions[address]['seq']}".encode('utf-8'), address)
        # print(len(sessions[address]['received']), sessions[address]['size'])
        if len(sessions[address]['received']) == sessions[address]['size']:
            sessions[address]['finished'] = True
            print("File received, writing out.")
            output = os.path.join(file_directory,
                                  f"{sessions[address]['filename']}.{sessions[address]['extension']}")

            with open(output, 'wb') as f:
                f.write(sessions[address]['received'])
    sessions_lock.release()
    time.sleep(0.1)
