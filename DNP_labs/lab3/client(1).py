import socket
import os
import io

server_address = ('127.0.0.1', 1234)
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# sock.setblocking(False)

file_directory = './client_data'
file_name = '61.jpg'
seq0 = 0
# file = open(os.path.join(file_directory, file_name), 'rb')
file_array = b""
with open(os.path.join(file_directory, file_name), 'rb') as f:
    byte = f.read(1)
    file_array += byte
    while byte != b"":
        byte = f.read(1)
        file_array += byte

file_size = len(file_array)


def get_file_extension(filename):
    return filename.split('.')[-1]


extension = get_file_extension(file_name)
# Initiate connection to the server

msg = f's|{seq0}|{extension}|{file_size}'
print(msg)

sock.sendto(msg.encode('utf-8'), server_address)
seq = seq0

# First ack
msg, address = sock.recvfrom(1024)

# Parse the ack
msg = msg.decode('utf-8').split('|')
print("Initial ack received. Starting file transfer.")

if msg[0] != 'a' or int(msg[1]) != seq + 1:
    exit(1)

server_buff_size = int(msg[2])
seq += 1
retries = 0
while True:
    chunk = file_array[:server_buff_size]
    msg = f'd|{seq}|'
    # print(chunk)
    # print(msg.encode('utf-8')+chunk)
    sock.sendto(msg.encode('utf-8')+chunk, server_address)
    retries += 1
    sock.settimeout(0.5)
    try:
        msg, address = sock.recvfrom(1024)
        retries = 0
    except socket.timeout:
        print("ACK timed out.")
        if retries == 5:
            exit(1)
        continue
    # Parse the ack
    msg = msg.decode('utf-8').split('|')
    # print(msg)
    # print(seq)
    if msg[0] != 'a' or int(msg[1]) != seq + 1:
        exit(1)
    file_array = file_array[server_buff_size:]
    seq += 1
    if file_array == b"":
        break

print("File transfer done.")
