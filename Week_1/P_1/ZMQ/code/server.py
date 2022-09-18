import sys
import zmq
import helper as h

# constants for local use
CLIENT_IN = 5555
CLIENT_OUT = 5556
WORKER_IN = 8888
WORKER_OUT = 8889


def server(c_in: int, c_out: int, w_in: int, w_out: int):
    # define the general context
    c_in_context = zmq.Context()
    # socket for user input
    c_in_socket = c_in_context.socket(zmq.REP)
    c_in_socket.bind(h.bind_string(c_in))

    # socket for user output
    c_out_context = zmq.Context()
    c_out_socket = c_out_context.socket(zmq.PUB)
    c_out_socket.bind(h.bind_string(c_out))

    # socket for worker input
    w_in_context = zmq.Context()
    w_in_socket = w_in_context.socket(zmq.PUB)
    w_in_socket.bind(h.bind_string(w_in))

    # socket for worker output
    w_out_context = zmq.Context()
    w_out_socket = w_out_context.socket(zmq.SUB)
    w_out_socket.connect(h.connect_string(w_out))
    w_out_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        try:
            req = c_in_socket.recv_string()
            print(f"processing request: {req}")

            if h.is_valid_request(req):
                print("valid request")
                print("pass to our back servers")
                w_in_socket.send_string(req)
                print("waiting for a reply from back servers")
                reply = w_out_socket.recv_string()
                print(f"The servers replied with {reply}")
                print("sending the reply")
                c_in_socket.send_string(reply)

            elif req:
                print("the request does not follow the format")
                print("sending back as it is")
                # c_out_socket.send_string(req)
                c_in_socket.send_string(req)
        except zmq.Again:
            pass


def main():
    args = sys.argv
    if len(args) == 5:  # the file name, and the two ports
        c_in = int(args[1])
        c_out = int(args[2])
        w_in = int(args[3])
        w_out = int(args[4])
        server(c_in, c_out, w_in, w_out)
    else:
        server(CLIENT_IN, CLIENT_OUT, WORKER_IN, WORKER_OUT)


if __name__ == "__main__":
    main()
