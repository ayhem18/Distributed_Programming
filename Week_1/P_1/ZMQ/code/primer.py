import sys
import helper as h
from server import WORKER_IN, WORKER_OUT
import re

PRIMER_FILTER = "isprime"


def prime_reply(request: str):
    num = int(re.split(r'\s+', request)[1])
    return f"{str(num)} is {'' if h.is_prime(num) else 'not'} prime"


def primer(in_port: int, out_port: int):
    h.back_server(in_port, out_port, prime_reply, PRIMER_FILTER)


def main():
    args = sys.argv
    if len(args) == 3:  # the file name, and the two ports
        i_p = int(args[1])
        o_p = int(args[2])
        primer(i_p, o_p)
    else:
        primer(WORKER_IN, WORKER_OUT)


if __name__ == "__main__":
    main()
