import zmq
import sys

# constants for local use
CLIENT_IN = 5555
CLIENT_OUT = 5556
WORKER_IN = 8888
WORKER_OUT = 8889


def server(c_in: int, c_out: int, w_in: int, w_out: int):
    # define the general context
    context = zmq.Context()

    # socket for user input
    c_in_socket = context.socket(zmq.REP)
