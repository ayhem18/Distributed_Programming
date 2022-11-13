import sys
import re
import socket as sk
from server_mid import BUFFER_SIZE


def main(port: int, server_add: tuple):
    with sk.socket(sk.AF_INET, sk.SOCK_DGRAM) as client_s:
        try:
            client_s.bind(('localhost', port))

            while True:
                user_input = input("Please enter your command\n").strip().lower()

                put_pattern = r'put(\s)+(\S)+'
                if re.match(put_pattern, user_input) is not None or user_input == 'size' \
                        or user_input == 'pick' or user_input == 'pop':
                    message = user_input
                    client_s.sendto(message.encode(), server_add)
                    data, address = client_s.recvfrom(BUFFER_SIZE)
                    print(f"{data.decode()}")
                else:
                    print("Please make sure to write a valid command")

        except KeyboardInterrupt:
            print("Client shutting down..")
            sys.exit()


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:  # make sure the port number is passed
        main(int(args[1]), ("127.0.0.1", 5000))
    else:
        main(8000, ("127.0.0.1", 5000))
