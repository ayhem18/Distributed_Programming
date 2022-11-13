import sys

import raft_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures
import os
import raft_pb2 as pb2
import re
import random
from test_timer import RepeatedTimer

MAX_WORKERS = 10
DEFAULT_PORT = 5555

# set a seed for random functionality for reproducible results
random.seed(0)
MIN_SEL_TIMEOUT = 0.150  # in ms
MAX_SEL_TIMEOUT = 0.301  # is ms
HEARTBEAT_TIMEOUT = 5


def negate(value):
    if isinstance(value, bool):
        return not value
    return False


class Server(pb2_grpc.serverServicer):
    CONFIG_FILE_NAME = "config.conf"
    # states
    FOLLOWER = 'follower'
    CANDIDATE = "candidate"
    LEADER = "leader"

    def get_address(self, server_id: int):
        curr_dir = os.getcwd()
        path = os.path.join(curr_dir, self.CONFIG_FILE_NAME)

        with open(path, 'r') as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines]
            servers_info = {}
            my_server_addr, my_server_id = None, None
            for line in lines:
                line_id, server_address, port = re.split(r"\s+", line)
                server_address = server_address + ":" + port
                servers_info[int(line_id)] = server_address
                if line_id.isnumeric() and int(line_id) == server_id:
                    my_server_addr = server_address
                    my_server_id = server_id

        if my_server_id is None:
            raise KeyError(f"The given id: {str(server_id)} is not present in the file!!!")

        return my_server_id, my_server_addr, servers_info

    def __init__(self, server_id: int, term: int = 0, is_leader: bool = False):
        # set the server's address, id, as well as the total number of servers in the system
        self.server_id, self.server_address, self.servers_info = self.get_address(server_id)
        # set the selection timeout
        self.selection_timeout = random.uniform(MIN_SEL_TIMEOUT, MAX_SEL_TIMEOUT)
        # set the term
        self.term = term
        self.state = self.FOLLOWER
        # first set to None as no server is initially a leader
        self.leader_timer = None

        # let's create the leader related fields
        self.current_leader_info = {}  # a dictionary to save the information about the current leader
        self.votes = []  # a list created to save the ids of servers that voted for this server as a candidate

        if is_leader:
            self.become_leader()

    def _leader_function(self):
        """
        # this function is to be called by the leader_timer object every 50 ms.
        :return: boolean: if the server should stay as a leader or not
        """
        for s_id, s_addr in self.servers_info.items():
            if s_id == self.server_id:
                continue
            channel = grpc.insecure_channel(s_addr)
            # set the stub
            leader_stub = pb2_grpc.serverStub(channel)
            # send the heartbeat
            # send the server's term and server's id
            append_request = pb2.AppendRequest(term=self.term, leader_id=self.server_id)
            server_reply = leader_stub.appendEntries(append_request)
            # if the term sent by the follower is larger than the server's
            if not server_reply.result:
                self.term = server_reply.term
                return False

        return True

    def become_leader(self):
        self.state = self.LEADER
        self.leader_timer = RepeatedTimer(HEARTBEAT_TIMEOUT, self._leader_function, negate)

    def suspend(self, request, context):
        pass

    def getLeader(self, request, context):
        pass

    def requestVote(self, request, context):
        pass

    def appendEntries(self, request, context):

        leader_term = request.term
        leader_id = request.leader_id
        print(f"leader_term:\t{str(leader_term)}")
        print(f"leader_id:\t{str(leader_id)}")
        reply = pb2.AppendReply(term=max(leader_term, self.term), result=leader_term >= self.term)
        return reply


def main(server_id: int = 1, term=0, is_leader=False):
    try:
        server = Server(server_id, term, is_leader)
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
    if len(args) >= 4:
        s_id = int(args[1])
        s_term = int(args[2])
        leader = args[3] == '1'
        main(s_id, s_term, leader)

