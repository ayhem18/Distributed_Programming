# Client's side

# imports
import os
import socket as sk
import sys
import checker as ch

# constants used through the script
server_error_msg = "SERVER UNAVAILABLE"
sk_creation_error_msg = "ERROR WHILE CREATING SOCKET"
remote_ip = "127.0.0.1"

client_time_out_count = 5  # the number of times the client will set a timeout before terminating the session
client_time_out = 0.5
client_buffer_size = 4096


def create_start_packet(seq_num: int, file_name: str, file_size: int) -> bytes:
    msg_str = ch.delimiter.join([ch.start_code, str(seq_num), file_name, str(file_size)])
    return msg_str.encode()


def create_data_packet(seq_num: int, data: bytes) -> bytes:
    return ch.get_bytes(ch.data_code + ch.delimiter + str(seq_num) + ch.delimiter) + data


def trans_file(server_addr, file: os.path, file_name_server: str):
    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as client_s:
        # prepare for starting the session
        first_seq_num = 0
        file_size = os.path.getsize(file)
        client_s.settimeout(client_time_out)

        attempts = 0  # number of attempts to establish connection with server
        while attempts < client_time_out_count:
            try:
                start_pack = create_start_packet(first_seq_num, file_name_server, file_size)
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

                if attempts == client_time_out_count:
                    print(server_error_msg)
                    f.close()  # close the file
                    client_s.close()  # close the socket
                    sys.exit()

                next_seq = int(reply[1])
                index = next_index
        print("File transferred correctly!!")
        client_s.close()


def main():
    args = sys.argv
    server_addr = (args[1].split(":")[0], int(args[1].split(":")[1]))
    file = args[2]
    file_name = args[3]
    trans_file(server_addr, file, file_name)


if __name__ == "__main__":
    main()
