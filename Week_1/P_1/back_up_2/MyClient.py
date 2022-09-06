# Client's side

# imports
import os
import socket as sk
import sys
import time

import checker as ch

# constants used through the script

server_error_msg = "SERVER UNAVAILABLE"
sk_creation_error_msg = "ERROR WHILE CREATING SOCKET"
remote_ip = "127.0.0.1"

client_time_out_count = 5  # the number of times the client will set a timeout before terminating the session
# client_time_out = 3 * 60 * 1000  # the length of the time-out
client_time_out = 0.5
client_buffer_size = 4096


def create_start_packet(seq_num: int, file_name: str, file_size: int) -> bytes:
    msg_str = ch.delimiter.join([ch.start_code, str(seq_num), file_name, str(file_size)])
    return msg_str.encode()


def create_data_packet(seq_num: int, data: bytes) -> bytes:
    # data_str = data.decode()
    # msg_str = ch.delimiter.join([ch.data_code, str(seq_num), data_str])
    return ch.get_bytes(ch.data_code + ch.delimiter + str(seq_num) + ch.delimiter) + data
    # return ch.data_code.encode() + ch.delimiter.encode() + str(seq_num).encode() + ch.delimiter.encode() + data
    # return msg_str.encode()


def trans_file(server_addr, file: os.path, file_name_server: str):
    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as client_s:
        # prepare for starting the session
        # server_addr = (remote_ip, port)
        first_seq_num = 0
        file_size = os.path.getsize(file)
        client_s.settimeout(client_time_out)

        print(server_addr)
        ### start of send the start message to the server
        # for _ in range(client_time_out_count):
        #     client_s.sendto(create_start_packet(first_seq_num, file_name_server, file_size), server_addr)
        #     server_reply, ser_add = client_s.recvfrom(client_buffer_size)
        #
        #     if server_reply:  # if the socket received a packet
        #         server_reply = ch.verify_ack_start(server_reply)  # verify whether the message is semantically valid
        #
        #         if server_reply is not None:
        #             # verify that the acknowledgement sent by the server
        #             # is up-to-date as well as the semantics of the server's message
        #
        #             if int(server_reply[1]) != first_seq_num:
        #                 break
        #     print("received ack for start session from {add}".format(add=server_addr))
        ### end of the send start message part

        ## start of send the start message to server
        attempts = 0  # number of attempts to establish connection with server
        while attempts < client_time_out_count:
            try:
                start_pack = create_start_packet(first_seq_num, file_name_server, file_size)
                print(start_pack)
                client_s.sendto(start_pack, server_addr)
                server_reply, ser_add = client_s.recvfrom(client_buffer_size)
                server_reply = ch.verify_ack_start(server_reply)  # verify whether the message is semantically valid

                if server_reply is not None:
                    # verify that the acknowledgement sent by the server
                    # is up-to-date as well as the semantics of the server's message
                    if int(server_reply[1]) != first_seq_num:
                        break
            except sk.timeout:  # this means that the client did not receive anything for ~ 1 second
                attempts += 1


        # if the session was not established in the first place
        if attempts == client_time_out_count:
            print(server_error_msg)
            client_s.close()
            sys.exit()

        # if we reached this part of the code, it means the connection was established
        next_seq, server_buffer_size = server_reply[1:]  # the first and second elements of the reply
        next_seq = int(next_seq)
        server_buffer_size = int(server_buffer_size)

        # sending the chunks of data
        index = 0

        while index < file_size:
            with open(file, 'rb') as f:
                next_index = min(file_size, index + server_buffer_size - ch.data_msg_header_size(next_seq))
                data_bytes = f.read()[index: next_index]

                attempts = 0
                while attempts < client_time_out_count:
                    try:
                        client_s.sendto(create_data_packet(next_seq, data_bytes), server_addr)
                        server_reply, ser_add = client_s.recvfrom(client_buffer_size)

                        reply = ch.verify_ack_data(server_reply)
                        # verify that the acknowledgement sent by the server is up-to-date and the message is valid
                        # if the ack message is for the previous packet, then both seq numbers will be the same

                        if reply is not None:  # if the reply satisfies the protocol's criteria
                            if int(reply[1]) == next_seq + 1:  # if the sequence number is increased by 1
                                break  # return a list containing the components of the server's reply
                    except sk.timeout:
                        attempts += 1
                        print("timeout: " + str(first_seq_num))
                        print("attempt: " + str(attempts))

                if attempts == client_time_out_count:
                    print(server_error_msg)
                    f.close()  # close the file
                    client_s.close()  # close the socket
                    sys.exit()

                print("sending the chunk of data at index {i} to server successfully".format(i=str(index)))
                next_seq = int(reply[1])
                index = next_index
        client_s.close()


def main():
    args = sys.argv
    print(args)
    server_addr = (args[1].split(":")[0], int(args[1].split(":")[1]))
    file = args[2]
    file_name = args[3]
    trans_file(server_addr, file, file_name)


def main1():
    file = os.path.join("me.JPG")
    trans_file(8884, file, "f1.JPG")


if __name__ == "__main__":
    main()
