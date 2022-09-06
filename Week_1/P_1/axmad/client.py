import socket

UDP_IP = "localhost"
UDP_PORT = 9999
ENCOD = "UTF-8"
WAIT_TIME = 3
BUFFSIZE = 1024

def parse_message_from_server(message):
    prefix, rest = message.split(" | ".encode(ENCOD), 1)

    # # prefix gonna be b"d"
    seqno, bufsize = rest.split(" | ".encode(ENCOD), 1)
    
    prefix = prefix.decode(ENCOD)
    seqno = int(seqno.decode(ENCOD))
    bufsize = int(bufsize.decode(ENCOD))

    return prefix, seqno, bufsize



# establish udp connection

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.settimeout(WAIT_TIME)


# send start message from client to server
# "s | seqno_0 | filename | size "

filee = open("../test_files/test.png", "rb").read()

seqno_0 = 0
filename = "amad.png"
file_size = len(filee)

server_bufsize = 1024

start_msg = f"s | {seqno_0} | {filename} | {file_size}"

# print(file[0])

sock.sendto(start_msg.encode(ENCOD), (UDP_IP, UDP_PORT))

# wait for acknowledgement for start
while True:
    message, address = sock.recvfrom(BUFFSIZE)

    prefix, seqno, bufsize = parse_message_from_server(message)
    
    if prefix == "a":
        seqno_0 = seqno
        server_bufsize = bufsize
        break
    
    sock.sendto(start_msg.encode(ENCOD), (UDP_IP, UDP_PORT))

# send data to server
# "d | seqno_0+1 | data-bytes"
cur_data_idx = 0
while cur_data_idx < file_size:
    # send a chunk
    data_message = f"d | {seqno_0} | "
    next_data_idx = min(cur_data_idx + server_bufsize - len(data_message), file_size)
    data_message = data_message.encode(ENCOD)
    data_message += filee[cur_data_idx : next_data_idx]

    sock.sendto(data_message, (UDP_IP, UDP_PORT))

    message, address = sock.recvfrom(BUFFSIZE)

    prefix, seqno, bufsize = parse_message_from_server(message)
    
    if prefix == "a":
        cur_data_idx = next_data_idx
        seqno_0 = seqno
        server_bufsize = bufsize
    

    


# # bind using specific network interface to specific port
# s.bind((address, port))

# # use any available port
# s.bind(('', 0))
# msg, client_address = s.recvfrom(BUFFSIZE)
# s.sendto(message, client_address)

# packet = f"d | {seqno} | ".encode() + data_chunk
# prefix, rest = packet.split(" | ".encode(), 1)

# # prefix gonna be b"d"
# seqno, data = rest.split(" | ".encode(), 1)
# seqno = int(seqno.decode())