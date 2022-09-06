import os
import socket as sk
import time

import checker as ch
import sys

# let's define the dictionary where clients' information will be saved
# the dictionary will save:

# * addr: client's address
# * file_name: the filename as saved in the server
# * last_seq_num: the last sequence number in an approved message: to avoid writing the same data twice
# * last_time_stamp: the last time the client interacter with a server: to remove inactive clients

clients = {}
# a set of files
files = set(())

# constants for the names used in the clients' dictionaries fields
c_addr = "address"
c_f = "file_name"
c_seq = "seq_number"
c_l_seq = "last_seq_num"
c_time = "last_time_stamp"
c_data = "data"
c_f_z = "file_size"

buffer_size = 4096  # the side of data accepted at each transfer
ip = '127.0.0.1'


# def receive_start_packet(address, data_received:bytes) -> dict:
#     # a start packet is accepted if the message follows the semantics of the protocol and
#     # the file name is unique
#     client_start = ch.verify_start_msg(data_received)

#     if client_start is not None : # if it is None then the semantics were not respected
#         file_name = create_local_file_name(address, client_start[2])

#         if file_name in files:
#             return None

#         else:
#             files.add(file_name)
#             client_packet =
#             {c_addr:address, c_f: file_name, c_seq: client_start[1], c_time: time.now(), is_data:False}
#             return client_packet

#     return None

# def receive_data_packet(address, data_received: bytes) -> dict:
#     # the only constraint on data packets are the protocol semantics
#     client_data = ch.verify_data_msg(data_received)

#     if client_data is not None:
#         c

#     return None


# def start_packet(packet: dict) -> dict:
#     # ensuring a duplicated start packet would not
#     if packet[c_addr] not in clients:
#         # initiate the client
#         clients[packet[c_addr]] = {}
#         # save last sequence number
#         clients[packet[c_addr]][c_l_seq] = packet[c_seq]
#         # save the name used in the server
#         clients[packet[c_addr]][c_f] = create_local_file_name(packet)

#     # save the last timestamp: important to evaluate whether the client is active or not
#     clients[packet[c_addr]][c_time] = time.now()


# def write_data_packet(file_name:os.path, data:bytes):
#     with open(file_name, 'a') as f:
#         f.write(data)


# def data_packet(packet: dict) -> dict:
#     # get the address of the packet
#     addr = packet[c_addr]

#     # set the new last timestamp
#     clients[addr][c_time] = time.now()

#     # get the seq_number
#     seq_num = packet[c_seq]
#     # get the data
#     data = packet[c_data]

#     # get the last seq number saved
#     last_seq_num = clients[addr][c_l_seq]

#     # if the two sequence numbers are the same, then the packet is not up-to-date
#     if last_seq_num != seq_num:
#         # get the filename
#         file_name = clients[addr][c_f]
#         write_data_packet(file_name, data)

def local_file_name(client_addr: tuple, client_file_name: str) -> os.path:
    # the final name would be "wd/address_filename" to limit collisions 
    working_dir = os.getcwd()
    return os.path.join(working_dir, "_".join([str(client_addr), client_file_name]))


def add_client(address: tuple, seq_num: int, file_name: os.path, file_size: int):
    if address not in clients:  # only apply the following to new (non-duplicate) start messages
        # initialize the new client info
        clients[address] = {}
        clients[address][c_f] = file_name
        clients[address][c_l_seq] = seq_num
        clients[address][c_f_z] = file_size
    # for duplicate start messages, we update the time stamp
    clients[c_time] = time.time()


def ack_start(seq_num: int) -> bytes:
    # return the next integer as a sequence number  (don't forget about the buffer size)
    ack_str = ch.delimiter.join([ch.ack_code, str(seq_num + 1), str(buffer_size)])
    return ack_str.encode()


def write_data_to_file(file_name: str, data: bytes):
    with open(file_name, 'ab') as f:  # open the file in append mode
        f.write(data)


def update_client(address: tuple, seq_num: int, file_name: os.path, data: bytes):
    if seq_num != clients[address][c_l_seq]:  # if both values are the same then this is a duplicated data message
        # first thing write (append) the data to the fil
        write_data_to_file(file_name, data)
        # second update the seq number
        clients[address][c_l_seq] = seq_num
    # regardless, update the last time stamp
    clients[c_time] = time.time()


def data_ack(seq_num: int):
    ack_str = ch.delimiter.join([ch.ack_code, str(seq_num + 1)])
    return ack_str.encode()


def receive_data(address, data: bytes):
    start_c = ch.verify_start_msg(data)  # stands for start components
    data_c = ch.verify_data_msg(data)  # stands for data components

    if start_c is not None:  # the message received is a start message
        seq_num = int(start_c[1])
        f = start_c[2]
        file_name = local_file_name(address, f)
        file_size = start_c[3]
        if file_name not in files:  # accept the session only if the file name is unique
            add_client(address, seq_num, file_name, file_size)
            return ack_start(seq_num)

    elif data_c is not None:  # the message received is a data message
        # get the sequence number of the data passed
        seq_num = int(data_c[1])
        file_name = clients[address][c_f]
        # keep in mind that the data passed in the data message is of type str:
        # the file_data should be converted to bytes to be written correctly to the file
        file_data = data_c[-1].encode()
        update_client(address, seq_num, file_name, file_data)
        return data_ack(seq_num)

    return None


def server(port: int):
    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as s:
        s.bind((ip, port))
        while True:
            data, addr = s.recvfrom(buffer_size)
            client_address = addr
            ack = receive_data(client_address, data)
            if ack is not None:
                s.sendto(ack, addr)


def main():
    args = sys.argv
    assert len(args) == 2  # make sure the port number is passed
    server(int(args[1]))


def main1():
    server(8888)


if __name__ == "__main__":
    main1()
