import socket as sk
import sys
from server import SERVER_REPLY_TRUE

CLIENT_NUMBERS = [15492781, 15492787, 15492803,
                  15492811, 15492810, 15492833,
                  15492859, 15502547, 15520301,
                  15527509, 15522343, 1550784]

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8888  # The port used by the server
CLIENT_BUF_SIZE = 2048


def display_respond(number: int, data: bytes):
    print("{num} is {pre} prime".format(num=number, pre="" if data.decode() == SERVER_REPLY_TRUE else "not"))


def client(serv_addr: tuple, numbers=None):
    if numbers is None:
        numbers = CLIENT_NUMBERS

    with sk.socket(sk.AF_INET, sk.SOCK_STREAM) as s:
        try:
            s.connect(serv_addr)
            for num in numbers:
                print("sending number :" + str(num))
                s.sendall(str(num).encode())

                data = s.recv(CLIENT_BUF_SIZE)

                display_respond(num, data)
            print("Completed")
            s.close()
        except:
            print("SERVER SHUT DOWN")


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        ser_add_str = args[1].split(":")
        server_address = (ser_add_str[0], int(ser_add_str[1]))
        client(server_address)
    else:
        client((HOST, PORT))
