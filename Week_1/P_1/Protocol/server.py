import sys

import service_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures
import service_pb2 as pb2
import re

MAX_WORKERS = 10
DEFAULT_PORT = 5555


# server's functionality for reverse command
class ReverseHandler(pb2_grpc.reverseServicer):
    def ReverseString(self, request, context):
        msg = request.text
        return pb2.ReverseReply(**{"message": msg[::-1]})


# server's functionality for split command
class SplitHandler(pb2_grpc.splitServicer):
    def splitString(self, request, context):
        text = request.text
        delimiter = request.delimiter
        split = re.split(delimiter, text)
        reply = {"number": len(split), "parts": split}
        return pb2.SplitReply(**reply)


# server's functionality for isprime command
class IsPrimeHandler(pb2_grpc.isPrimeServicer):
    def is_prime(self, request_iterator, context):
        for request in request_iterator:
            response = pb2.isPrimeReply(**{'number_primer': prime_checker(request.number)})
            yield response
            # yield request


def prime_checker(number):
    """returns True if number
    is prime, False otherwise"""
    result = True
    if number <= 1:
        # print_processing_msg(number)
        result = False
    elif number <= 3:
        # print_processing_msg(number)
        result = True
    elif number % 2 == 0:
        result = False
    else:
        for divisor in range(3, number, 2):  # skip even numbers: as a prime number (larger than 2) cannot be even
            if number % divisor == 0:
                # print_processing_msg(number)
                result = False
                break
        # print_processing_msg(number)

    return f"{str(number)} is {'' if result else 'not '}prime"


def main(port: int = DEFAULT_PORT):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_reverseServicer_to_server(ReverseHandler(), server)
    pb2_grpc.add_splitServicer_to_server(SplitHandler(), server)
    pb2_grpc.add_isPrimeServicer_to_server(IsPrimeHandler(), server)

    server.add_insecure_port(f"127.0.0.1:{str(port)}")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        main(int(args[1]))
    else:
        main()
