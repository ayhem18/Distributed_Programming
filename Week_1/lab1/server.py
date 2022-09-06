import socket

UDP_IP = 'localhost'#"<ip_address_of_receiver>"
UDP_PORT = 9999
MESSAGE = "Hi, can you listen to this?"
ENCOD = "UTF-8"
WAIT_TIME = 3
BUFFSIZE = 1024

def parse_start_from_client(message):

    prefix, rest = message.split(" | ".encode(ENCOD), 1)
    seqno, rest = rest.split(" | ".encode(ENCOD), 1)
    filename, file_size = rest.split(" | ".encode(ENCOD), 1)
    
    prefix = prefix.decode(ENCOD)
    seqno = int(seqno.decode(ENCOD))
    filename = filename.decode(ENCOD)
    file_size = int(file_size.decode(ENCOD))

    return prefix, seqno, filename, file_size

def parse_data_from_client(message):
    
    prefix, rest = message.split(" | ".encode(ENCOD), 1)
    seqno, data_bytes = rest.split(" | ".encode(ENCOD), 1)
    
    prefix = prefix.decode(ENCOD)
    seqno = int(seqno)
    data_bytes = bytes(data_bytes)

    return prefix, seqno, data_bytes


print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(WAIT_TIME)

started = False
filename = ""
seqno = 0
file_size = 0
client_addr = ""

while True:
    message, address = sock.recvfrom(BUFFSIZE)
    
    prefix, seqno, filename, file_size = parse_start_from_client(message)

    if prefix == "s":
        started = True
        client_addr = address
        message = f"a | {seqno + 1} | {BUFFSIZE}"
        sock.sendto(message.encode(ENCOD), client_addr)
        break

# port = 0

if started:
    print("Started connection")

bytes_to_save = b""

while len(bytes_to_save) < file_size:
    message, address = sock.recvfrom(BUFFSIZE)
    
    prefix, seqno, data_bytes = parse_data_from_client(message)

    if prefix == "d":
        print (f"received chunk {seqno}")
        message = f"a | {seqno + 1} | {BUFFSIZE}"
        sock.sendto(message.encode(ENCOD), client_addr)
        bytes_to_save += data_bytes    

filename = "(received) " + filename
filee = open(filename, "wb+").write(bytes_to_save)

