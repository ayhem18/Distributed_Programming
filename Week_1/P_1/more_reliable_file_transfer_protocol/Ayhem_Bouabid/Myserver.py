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
# * is_complete: the file transfer is complete

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
c_is_complete = "is_complete"

buffer_size = 4096  # the side of data accepted at each transfer
ip = '127.0.0.1'


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
        clients[address][c_is_complete] = False
    # for duplicate start messages, we update the time stamp
    clients[address][c_time] = time.time()


def ack_start(seq_num: int) -> bytes:
    # return the next integer as a sequence number  (don't forget about the buffer size)
    ack_str = ch.delimiter.join([ch.ack_code, str(seq_num + 1), str(buffer_size)])
    return ack_str.encode()


def write_data_to_file(file_name: str, data: bytes):
    with open(file_name, 'ab') as f:  # open the file in append mode
        f.write(data)
        f.close()


def update_client(address: tuple, seq_num: int, file_name: os.path, data: bytes):
    if seq_num == clients[address][c_l_seq] + 1:  # if both values are the same then this is a duplicated data message
        # first thing write (append) the data to the fil
        write_data_to_file(file_name, data)
        # second update the seq number
        clients[address][c_l_seq] = seq_num
        # print("just wrote data from {add} to file {f_name}".format(add=address, f_name=file_name))
        # if the current size is the same as the final size passed by the start message
        clients[address][c_is_complete] = (clients[address][c_f_z] == os.path.getsize(clients[address][c_f]))
    # regardless, update the last time stamp
    clients[address][c_time] = time.time()


def data_ack(seq_num: int):
    ack_str = ch.delimiter.join([ch.ack_code, str(seq_num + 1)])
    return ack_str.encode()


def receive_data(address, data: bytes):
    start_c = ch.verify_start_msg(data)  # stands for start components
    data_c = ch.verify_data_msg(data)  # stands for data components

    if start_c is not None:  # the message received is a start message
        # print("received start message from {add}".format(add=address))
        seq_num = int(start_c[1])
        file_name = local_file_name(address, start_c[2])
        file_size = int(start_c[3])
        if file_name not in files:  # accept the session only if the file name is unique
            add_client(address, seq_num, file_name, file_size)
            return ack_start(seq_num)

    elif data_c is not None:  # the message received is a data message
        # certain clients would be inactive for a long time
        # and get disconnected from the server, however they would still send data packets
        # those should not be considered
        # print("received data message from {add}".format(add=address))
        if address in clients:
            # get the sequence number of the data passed
            seq_num = int(data_c[1])
            file_name = clients[address][c_f]
            # keep in mind that the data passed in the data message is of type str:
            # the file_data should be converted to bytes to be written correctly to the file
            file_data = data_c[-1]
            update_client(address, seq_num, file_name, file_data)
            return data_ack(seq_num)

    return None


max_inactive_time = 3.2  # a session inactive for 3 seconds should be removed
save_complete_session = 1.2  # keep the information about a successful session before removing it


def remove_sessions():
    now = time.time()
    sessions_to_rmv = []
    for addr, client_info in clients.items():
        # remove session that were inactive for more than ~ 3 seconds
        if now - client_info[c_time] >= max_inactive_time:
            print("removing client with address {add} for being inactive".format(add=addr))
            sessions_to_rmv.append(addr)
        # if the session is complete: the size given in the start packet is equal to the size stored in the server
        # as well as the time constraint, then remove the session's info
        elif now - client_info[c_time] >= save_complete_session and client_info[c_is_complete]:
            print("removing client with address {add} after completing the session successfully".format(add=addr))
            sessions_to_rmv.append(addr)

    # remove the sessions

    for sess in sessions_to_rmv:
        clients.pop(sess)


def server(port: int):
    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as s:
        s.bind((ip, port))
        s.settimeout(save_complete_session)  # this will make the
        while True:
            try:
                data, addr = s.recvfrom(buffer_size)
                client_address = addr
                ack = receive_data(client_address, data)
                if ack is not None:
                    s.sendto(ack, addr)
                    # remove sessions after sending any ack
                    remove_sessions()
            except sk.timeout:
                remove_sessions()


def main():
    args = sys.argv
    assert len(args) == 2  # make sure the port number is passed
    server(int(args[1]))


if __name__ == "__main__":
    main()
