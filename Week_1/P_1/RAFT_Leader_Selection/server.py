import sys

import raft_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures
import os
import raft_pb2 as pb2
import re
import random
from timer import RepeatedTimer

MAX_WORKERS = 10

# set a seed for random functionality for reproducible results
random.seed(0)
MIN_SEL_TIMEOUT = 0.150  # in ms
MAX_SEL_TIMEOUT = 0.301  # is ms
HEARTBEAT_TIMEOUT = 5


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

    def __init__(self, server_id: int):
        # set the server's address, id, as well as the total number of servers in the system
        self.server_id, self.server_address, self.servers_info = self.get_address(server_id)
        # set the selection timeout
        self.selection_timeout = random.uniform(MIN_SEL_TIMEOUT, MAX_SEL_TIMEOUT)
        # set the term initially to zero
        self.term = 0
        self.state = self.FOLLOWER

        # this function should be called every selection_Timeout
        # however, it should be stopped when _candidate_function returns True
        self.candidate_timer = RepeatedTimer(self.selection_timeout, self._candidate_function,
                                             lambda x: x if isinstance(x, bool) else False)

        # this timer is responsible for putting an end to the elections if it takes more than selection_TIMEOUT
        # it should be started from the body of _candidate_function, stopped either by _candidate_function
        # if the candidate becomes a leader, or after stopping _candidate_function
        self.election_timer = RepeatedTimer(self.selection_timeout, self._track_election_function, lambda x: True)

        # set the leader_time: this timer will call the _leader_function every  HEARTBEAT_TIMEOUT
        # if the _leader_function returns False, this timer should be stopped
        self.leader_timer = RepeatedTimer(HEARTBEAT_TIMEOUT, self._leader_function,
                                          lambda x: not x if isinstance(x, bool) else False)

        # let's create the leader related fields
        self.current_leader_id = None
        self.term_leaders = {}  # this is a dictionary where each term maps to the id of its leader:
        # from the perspective of that server node

    def _track_election_function(self):
        """
        This function will be called by the election timer. It should stop the election as the timeout expires
        :return: None
        """
        # first of all this function will stop the candidate timer
        self.candidate_timer.stop()
        # set the state to FOLLOWER
        self.state = self.FOLLOWER
        # re-initialize the selection_timeout
        self.selection_timeout = random.uniform(MIN_SEL_TIMEOUT, MAX_SEL_TIMEOUT)
        self.candidate_timer.interval = self.selection_timeout
        # re-start the candidate timer as it should always run
        self.candidate_timer.start()

        # this timer will be closed either by finishing this call
        # (if the elections were not conducted within the time constraints)
        # or by _candidate_function if the elections take place successfully

    def _candidate_function(self):
        """
        This function will be called by the candidate timer
        :return:
        """
        # first of all: start the timeout_tracker
        self.election_timer.start()
        # first thing: set the state to CANDIDATE
        self.state = self.CANDIDATE
        # variable to store the number of votes: starting with 1: the node votes for itself.
        votes = 1
        # upgrade the term number
        self.term += 1
        # set the new leader to itself
        self.term_leaders[self.term] = self.server_id

        for id_ser, addr_ser in self.servers_info.items():
            if s_id == self.server_id:
                continue
            voting_channel = grpc.insecure_channel(addr_ser)
            # set the stub
            voting_stub = pb2_grpc.serverStub(voting_channel)
            # set the voting request
            voting_request = pb2.VoteRequest(term=self.term, candidateId=self.server_id)
            server_reply = voting_stub.requestVote(voting_request)
            # if the term sent by the follower is larger than the server's
            if not server_reply.result:
                # the term sent by the other node is larger: the term should be updated
                self.term = server_reply.term
                # the leader in this very particular moment is not known
                self.term_leaders[self.term] = None
                # set the state to Follower
                self.state = self.FOLLOWER
                # stop the elections' tracker
                self.election_timer.stop()
                return False
            else:
                # add this node's vote to the votes' count
                votes += 1
                if votes / len(self.servers_info) >= 0.5:
                    # if the majority of votes was collected:
                    # set the state to Leader
                    self.state = self.LEADER
                    # set the current leader information to the server's info
                    self.term_leaders[self.term] = self.server_id
                    # set the leader_timer to start
                    self.leader_timer.start()
                    # stop the election_timer
                    self.election_timer.stop()
                    return True
        return True

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


    def suspend(self, request, context):
        pass

    def getLeader(self, request, context):
        pass

    def requestVote(self, request, context):
        pass

    def appendEntries(self, request, context):
        # extract the information about the heartbeat message
        heartbeat_term = request.term
        heartbeat_id = request.leader_id
        print(f"leader_term:\t{str(heartbeat_term)}")
        print(f"leader_id:\t{str(heartbeat_id)}")

        reply = pb2.AppendReply(term=max(heartbeat_term, self.term), result=heartbeat_term >= self.term)

        # if the current state is LEADER:
        # this happens only when a server was a leader, was suspended, and now it is receiving heartbeats
        # from the new leader
        if self.state == self.LEADER:
            if heartbeat_term >= self.term:
                # update the term
                self.term = heartbeat_term
                # update the leader information
                self.term_leaders[self.term] = heartbeat_id
                # stop the leader timer: a new leader has raised
                self.leader_timer.stop()
                # set the follower state
                self.state = self.FOLLOWER
                # start the candidate timer:
                self.candidate_timer.start()
            # otherwise the current leader is the final leader and no change should take place
        else:
            # first stop the timer: the one responsible for becoming a candidate
            self.candidate_timer.stop()

            if self.term < heartbeat_term:
                # update the term number
                self.term = heartbeat_term
                # if the leader_term is larger than the server's, update the leader's information
                self.term_leaders[self.term] = heartbeat_id

            # set the state to FOLLOWER either way
            self.state = self.FOLLOWER

            # reset the timer again
            self.candidate_timer.start()

        return reply


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
        s_id = int(args[1])
        # s_term = int(args[2])
        # leader = args[3] == '1'
        main(s_id)
