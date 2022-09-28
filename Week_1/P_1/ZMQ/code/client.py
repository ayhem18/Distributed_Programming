import sys
import zmq
from helper import connect_string

INPUT_PORT = 5555
OUTPUT_PORT = 5556


def client(input_port: int, output_port: int):
    context = zmq.Context()
    # create a socket responsible for sending messages
    sending_socket = context.socket(zmq.REQ)
    # print("Connecting to the server: input side")
    sending_socket.connect(connect_string(input_port))

    # create a socket responsible for receiving replies from server
    # this socket is a subscriber
    receiving_socket = context.socket(zmq.SUB)
    # print("Connecting to the server: output side")
    receiving_socket.connect(connect_string(output_port))
    # subscribe (otherwise no messages will be received)
    # the subscriber should receive any possible string
    receiving_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    # 100 seconds time out
    receiving_socket.RCVTIMEO = 100

    try:
        while True:
            # prompt the user for input
            user_input = input("> ")
            myReply = False
            if len(user_input) != 0:
                # this means the user entered input
                # send the passed string to the input
                sending_socket.send_string(user_input)
                sending_socket.recv_string()

            try:
                # receive the reply from the server
                # print("enter 2nd while loop!!")
                server_reply = receiving_socket.recv_string()
                print(server_reply)
                # print(f"Server replied with : {server_reply}")

            except zmq.Again:
                pass

    # a keyboard Interrupt means the client is terminated
    except KeyboardInterrupt:
        print("\n Terminating client")
        sys.exit(0)


def main():
    args = sys.argv
    if len(args) == 3:  # the file name, and the two ports
        i_p = int(args[1])
        o_p = int(args[2])
        client(i_p, o_p)
    else:
        client(INPUT_PORT, OUTPUT_PORT)


if __name__ == "__main__":
    main()
