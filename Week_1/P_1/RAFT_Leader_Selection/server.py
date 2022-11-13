import sys

import raft_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures
import os
import raft_pb2 as pb2
import re
import random

MAX_WORKERS = 10
DEFAULT_PORT = 5555

# set a seed for random functionality for reproducible results
random.seed(0)
MIN_SEL_TIMEOUT = 150  # in ms
MAX_SEL_TIMEOUT = 300  # is ms


class Server(pb2_grpc.serverServicer):
    CONFIG_FILE_NAME = "config.conf"

    def get_address(self, server_id: int):
        curr_dir = os.getcwd()
        path = os.path.join(curr_dir, self.CONFIG_FILE_NAME)

        with open(path, 'r') as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines]
            total = len(lines)
            for line in lines:
                line_id, server_address, port = re.split(r"\s+", line)

                if line_id.isnumeric() and int(line_id) == server_id:
                    server_address = server_address + ":" + port
                    return server_id, server_address, total
        raise KeyError(f"The given id: {str(server_id)} is not present in the file!!!")

    def __init__(self, server_id: int):
        # set the server's address, id, as well as the total number of servers in the system
        self.server_id, self.server_address, total_servers = self.get_address(server_id)
        # set the selection timeout
        self.selection_timeout = random.randint(MIN_SEL_TIMEOUT, MAX_SEL_TIMEOUT)

    def suspend(self, request, context):
        pass

    def getLeader(self, request, context):
        pass


def main(server_id: int = 1):
    try:
        server = Server(server_id)
    except KeyError as msg:
        print(msg)
        sys.exit()

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb2_grpc.add_serverServicer_to_server(server, grpc_server)

    grpc_server.add_insecure_port(server.server_address)
    grpc_server.start()
    try:
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        main(int(args[1]))
    else:
        main()
