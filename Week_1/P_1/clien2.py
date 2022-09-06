import os
import socket as sk
import sys
from math import ceil

import checker as ch

# constants used through the script

server_error_msg = "SERVER UNAVAILABLE"
sk_creation_error_msg = "ERROR WHILE CREATING SOCKET"
remote_ip = "127.0.0.1"

client_time_out_count = 5  # the number of times the client will set a timeout before terminating the session
client_time_out = 500  # the length of the time-out

udp_max_header = 16  # an udp packet takes at most 16 bytes
client_buffer_size = 4096


def transfile(port: int, file: os.path, file_name_server: str):
    try:
        client_s = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    except sk.error:
        sys.exit()

    def create_start_packet(seq_num: int, file_name: str, file_size: int) -> bytes:
        msg_str = ch.delimiter.join([ch.start_code, str(seq_num), file_name, str(file_size)])
        return msg_str.encode()

    def send_start_packet(server_add: tuple, seq_num: int, file_name: str, file_size: int):
        # send 5 times with a timeout of 1 second

        for _ in range(client_time_out_count):
            client_s.sendto(create_start_packet(seq_num, file_name, file_size), server_add)
            client_s.settimeout(client_time_out)
            server_reply, ser_add = client_s.recvfrom(client_buffer_size)

            if server_reply:  # if the socket received a packet
                reply = ch.verify_ack_start(server_reply)  # verify whether the message is semantically valid

                # verify that the acknowledgement sent by the server
                # is up-to-date as well as the semantics of the server's message
                reply_seq_num = int(reply[1])

                if reply is not None and reply_seq_num != seq_num:
                    return reply

        return None

    def create_data_packet(seq_num: int, data: bytes) -> bytes:
        data_str = data.decode()
        msg_str = ch.delimiter.join([ch.data_code, str(seq_num), data_str])
        # return ch.data_code.encode() + ch.delimiter.encode() + str(seq_num).encode() + ch.delimiter.encode() + data
        return msg_str.encode()

    def send_data_packet(client_s, server_add: tuple, seq_num: int, data: bytes):
        for _ in range(client_time_out_count):
            client_s.sendto(create_data_packet(seq_num, data), server_add)
            client_s.settimeout(client_time_out)
            server_reply, ser_add = client_s.recvfrom(client_buffer_size)

            if server_reply:  # if the socket received a packet
                reply = ch.verify_ack_data(server_reply)  # if the packet falls under the conditions of the server

                # verify that the acknowledgement sent by the server is up-to-date and the message is valid
                # if the ack message is for the previous packet, then both seq numbers will be the same
                reply_seq_num = int(reply[1])

                if reply is not None and reply_seq_num != seq_num:  # return if the message is good
                    return reply  # return a list containing the components of the server's reply

        return None

    def initiate_connection(port: int, file: os.path, file_name_server: str):
        # prepare for starting the session
        server_addr = (remote_ip, port)
        seq_num = 0
        file_size = os.path.getsize(file)

        # receive the server's reply
        server_reply = send_start_packet(server_addr, seq_num, file_name_server, file_size)

        if server_reply is None:
            print(server_error_msg)
            client_s.close()
            return None

        # receive the components from the server's reply
        next_seq, buffer_size = server_reply[1:]  # the first and second elements of the reply
        next_seq = int(next_seq)
        buffer_size = int(buffer_size)
        tran_data_size = buffer_size - udp_max_header  # maximum bytes of data per transfer
        n_trans = ceil(file_size / tran_data_size)  # the number of transfers
        # return a dictionary with all the information necessary to complete the file transfer
        return {"socket": client_s, "port": port, "ip": remote_ip, "file": file, 'next_seq': next_seq,
                "tran_data_size": tran_data_size, "n_trans": n_trans, "file_size": file_size}

    initiate_connection(port, file, file_name_server)

    server_addr = (remote_ip, port)
    seq_num = 0
    file_size = os.path.getsize(file)

    # receive the server's reply
    server_reply = send_start_packet(server_addr, seq_num, file_name_server, file_size)

    if server_reply is None:
        print(server_error_msg)
        client_s.close()
        return None

    # receive the components from the server's reply
    next_seq, buffer_size = server_reply[1:]  # the first and second elements of the reply
    next_seq = int(next_seq)
    buffer_size = int(buffer_size)
    tran_data_size = buffer_size - udp_max_header  # maximum bytes of data per transfer
    n_trans = ceil(file_size / tran_data_size)  # the number of transfers

    with open(file, 'r') as f:  # this will guarantee closing the file
        for i in range(n_trans):
            # read the i-th chunk of data
            data_bytes = f.read()[i * tran_data_size: min((i + 1) * tran_data_size, file_size)]
            server_reply = send_data_packet(client_s, server_addr, next_seq, data_bytes.encode())  # send the packet
            if server_reply is None:
                print(server_error_msg)
                sys.exit()
            else:
                next_seq = int(server_reply[1])
    client_s.close()


# def main():
#     args = sys.argv
#     assert len(args) == 4  # make sure the correct number of arguments is passed
#
#     port = int(args[1])
#     file = os.path.join(args[2])
#     file_name_server = args[3]
#
#     transfer_file(port, file, file_name_server)

def main1():
    file = os.path.join("test_files", 't1.txt')
    transfile(8888, file, "f1.txt")


if __name__ == "__main__":
    main1()
