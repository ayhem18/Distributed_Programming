import sys
import re
import helper as h
from server import WORKER_IN, WORKER_OUT

GCD_ER_FILTER = "gcd"


def gcd_reply(request: str):
    a = int(re.split(r'\s+', request)[1])
    b = int(re.split(r'\s+', request)[2])
    return f"gcd for {str(a)} {str(b)} is {str(h.gcd(a, b))}"


def gcd_er(in_port: int, out_port: int):
    h.back_server(in_port, out_port, gcd_reply, GCD_ER_FILTER)


def main():
    args = sys.argv
    if len(args) == 3:  # the file name, and the two ports
        i_p = int(args[1])
        o_p = int(args[2])
        gcd_er(i_p, o_p)
    else:
        gcd_er(WORKER_IN, WORKER_OUT)


if __name__ == "__main__":
    main()
