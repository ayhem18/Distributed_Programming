import math
import re

import zmq

from primer import PRIMER_FILTER
from gcd import GCD_ER_FILTER
from math import floor

def connect_string(port: int):
    return "tcp://localhost:{p}".format(p=str(port))


def bind_string(port: int):
    return "tcp://*:{p}".format(p=str(port))


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    elif n in [2, 3]:
        return True
    elif n % 2 == 0:
        return False

    upper_lim = math.ceil(math.sqrt(n))
    for i in range(3, upper_lim + 1, 2):
        if n % i == 0:
            return False

    return True


def gcd(a: int, b: int) -> int:
    if a < 0 or b < 0:
        return gcd(int(abs(a)), int(abs(b)))

    if a == 0 or b == 0:
        return max(a, b)

    if a == 1 or b == 1:
        return 1

    min_num = min(a, b)
    max_num = max(a, b)
    return gcd(max_num - floor(max_num / min_num) * min_num, min_num)


def is_valid_request(string: str):
    primer_regex = PRIMER_FILTER + r'[\s]+(-){0,1}[\d]+'
    gcd_er_regex = GCD_ER_FILTER + r'[\s]+(-){0,1}[\d]+[\s](-){0,1}[\d]+'
    primer_match = re.match(primer_regex, string)
    gcd_er_match = re.match(gcd_er_regex, string)

    if primer_match is None and gcd_er_match is None:
        return False
    if primer_match:
        return primer_match.end() - primer_match.start() == len(string)

    return gcd_er_match.end() - gcd_er_match.start() == len(string)


def back_server(in_port: int, out_port: int, reply_function, str_filter: str):
    # create context for receiving data
    sub_context = zmq.Context()

    # create a subscriber socket
    sub_socket = sub_context.socket(zmq.SUB)
    # connect to the input workers
    sub_socket.connect(connect_string(in_port))
    # set the filter
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, str_filter)

    sub_socket.RCVTIMEO = 100
    # create context for sending data
    pub_context = zmq.Context()

    # create the publisher socket: sending the results of requests
    pub_socket = pub_context.socket(zmq.PUB)
    pub_socket.connect(connect_string(out_port))

    while True:
        try:
            try:
                request = sub_socket.recv_string()
            except zmq.Again:
                continue

            print(f"received {request}")
            try:
                rep_req = reply_function(request)
            except:
                continue
            pub_socket.send_string(rep_req)
            print(f'sent the {rep_req}')
        except zmq.Again:
            pass


