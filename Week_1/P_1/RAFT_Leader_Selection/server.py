import sys
import threading as th
import raft_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures
import os
import raft_pb2 as pb2
import re
import random
from timer import RepeatedTimer
from timer import close_timer

MAX_WORKERS = 10

# set a seed for random functionality for reproducible results
# random.seed(0)

MIN_SEL_TIMEOUT = 0.15  # 150 ms
MAX_SEL_TIMEOUT = 0.30  # 300 ms
HEARTBEAT_TIMEOUT = 0.50  # 50 ms


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

        # self.candidate_timer = th.Timer(self.selection_timeout, self._candidate_function)


        # self.candidate_timer = RepeatedTimer(1, self._candidate_function,
        #                                      lambda x: x if isinstance(x, bool) else False)


        # this timer is responsible for putting an end to the elections if it takes more than selection_TIMEOUT
        # it should be started from the body of _candidate_function, stopped either by _candidate_function
        # if the candidate becomes a leader, or after stopping _candidate_function

        # self.election_timer = RepeatedTimer(self.selection_timeout, self._track_election_function, lambda x: True)

        self.election_tracker = th.Timer(self.selection_timeout, self._track_election_function)

        # set the leader_time: this timer will call the _leader_function every  HEARTBEAT_TIMEOUT
        # if the _leader_function returns False, this timer should be stopped
        self.leader_timer = RepeatedTimer(HEARTBEAT_TIMEOUT, self._leader_function,
                                          lambda x: not x if isinstance(x, bool) else False)

        # let's create the leader related fields
        self.current_leader_id = None
        # this is a dictionary where each term maps to the id of its leader:
        # from the perspective of that server node
        self.term_leaders = {0: None}
        # there is no leader in the first term and this should be set
        # make sure to start the candidate timer
        # print("starting the candidate timer")
        self.candidate_timer.start()
        # this variable is used when the client class suspend
        self.sleep = False
        self._summary()
        # print(f"The server starts at {str(self.server_address)}")
        # print(f"I am a {self.state}. Term: {str(self.term)}")

    def _summary(self):
        print("#" * 30)
        print(f"SERVER'S ID: {str(self.server_id)}")
        print(f"SERVER'S TERM: {str(self.term)}")
        print(f"SERVER'S STATE: {str(self.state)}")
        print(f"SELECTION TIMOUT: {str(self.selection_timeout)}")
        for term, s_id in self.term_leaders.items():
            print(f"term {str(term)}:\t {str(s_id)}")
        print()

    def _track_election_function(self):
        """
        This function will be called by the election timer. It should stop the election as the timeout expires
        :return: None
        """
        # time.sleep(self.selection_timeout)
        print("THE TIME FOR COLLECTING VOTES expired")
        # first of all this function will stop the candidate timer
        # print("The election timer stopping the candidate timer")
        self.candidate_timer.stop()
        # set the state to FOLLOWER
        self.state = self.FOLLOWER
        # re-initialize the selection_timeout
        print("CHANGING TIMEOUT")
        self.selection_timeout = random.uniform(MIN_SEL_TIMEOUT, MAX_SEL_TIMEOUT)
        self.candidate_timer.interval = self.selection_timeout
        # re-start the candidate timer as it should always run
        # print("starting the candidate timer from election tracker")
        self.candidate_timer.start()

        # this timer will be closed either by finishing this call
        # (if the elections were not conducted within the time constraints)
        # or by _candidate_function if the elections take place successfully

    def _become_leader(self):
        print("Votes received")
        # if the majority of votes was collected:
        # set the state to Leader
        self.state = self.LEADER
        # set the current leader information to the server's info
        self.term_leaders[self.term] = self.server_id
        # set the leader_timer to start
        self.leader_timer.start()
        # stop the election tracker
        self.election_tracker.cancel()
        print(f"I am a leader. Term: {str(self.term)}")
        # print(f"state after requesting votes from {str(id_ser)}")
        self._summary()

    def _candidate_function(self):
        """
        This function will be called by the candidate timer
        :return:
        """
        print("The leader is dead")
        # self.election_timer.start()
        self.election_tracker = th.Timer(self.selection_timeout, self._track_election_function)
        # set the state to CANDIDATE
        self.state = self.CANDIDATE
        # variable to store the number of votes: starting with 1: the node votes for itself.
        votes = 1
        # upgrade the term number
        # print(f"Upgrading the term to {str(self.term + 1)}")
        self.term += 1
        # set the new leader to itself
        # self.term_leaders[self.term] = self.server_id
        print(f"I am a candidate . Term: {str(self.term)}")
        print(f"Voted for node {str(self.server_id)}")

        # num_active_servers = len(self.servers_info)

        for id_ser, addr_ser in self.servers_info.items():
            if id_ser == self.server_id:
                continue

            voting_channel = grpc.insecure_channel(addr_ser)
            # set the stub
            voting_stub = pb2_grpc.serverStub(voting_channel)
            # set the voting request

            try:
                voting_request = pb2.VoteRequest(term=self.term, candidateId=self.server_id)
                server_reply = voting_stub.requestVote(voting_request)
                # if the term sent by the follower is larger than the server's
                # self._summary()
                print(f"vote result from {str(id_ser)} is {str(server_reply.result)} with term number"
                      f" {str(server_reply.term)}")

                if not server_reply.result:
                    # the term sent by the other node is larger: the term should be updated
                    self.term = server_reply.term
                    # the leader in this very particular moment is not known
                    self.term_leaders[self.term] = None
                    # set the state to Follower
                    self.state = self.FOLLOWER
                    # stop the elections' tracker
                    # print("the candidate did not win the election: stopping the election timer")
                    # self.election_timer.stop()
                    self.election_tracker.cancel()
                    # print(f"state after requesting votes from {str(id_ser)}")
                    # self._summary()
                    return False
                else:
                    # add this node's vote to the votes' count
                    votes += 1
                    if votes > len(self.servers_info) * 0.5:
                        self._become_leader()
                        return True

            except Exception:
                # print(f"server {str(id_ser)} with address {str(addr_ser)} is not available when voting")
                # num_active_servers -= 1
                pass
            # consider the case when the only active node is this node
            if votes > len(self.servers_info) * 0.5:
                self._become_leader()
                return True

        return False

    def _leader_function(self):
        """
        # this function is to be called by the leader_timer object every 50 ms.
        :return: boolean: if the server should stay as a leader or not
        """
        # print(f"I am a leader. Term: {str(self.term)}")
        # print("as the server is now a leader: stopping candidate and election tracker timers")
        self.candidate_timer.stop()
        for s_id, s_addr in self.servers_info.items():
            if s_id == self.server_id:
                continue
            try:
                channel = grpc.insecure_channel(s_addr)
                # set the stub
                leader_stub = pb2_grpc.serverStub(channel)
                # send the heartbeat
                # send the server's term and server's id
                append_request = pb2.AppendRequest(term=self.term, leader_id=self.server_id)
                server_reply = leader_stub.appendEntries(append_request)

                # print(f"receiving heart beat reply from {str(s_id)} with result: {str(server_reply.result)} "
                #       f"and term {str(server_reply.term)}")

                # if the term sent by the follower is larger than the server's
                if not server_reply.result:
                    # update the term
                    # print(f"updating term to {str(server_reply.term)}")
                    self.term = server_reply.term
                    # the current leader is unknown
                    self.term_leaders[self.term] = None
                    #  set the state to follower
                    self.state = self.FOLLOWER
                    self._summary()
                    # start the candidate timer
                    # print("starting the candidate timer as the leader is no longer valid")
                    self.candidate_timer.start()
                    return False

            except Exception:
                # print(f"server {str(s_id)} with address {str(s_addr)} is not available for heartbeats")
                pass
        return True

    def _wake_up(self):
        self.sleep = False
        # if the server used to be a leader it continues acting (temporarily as a leader)
        if self.state == self.LEADER:
            self.leader_timer.start()
        # otherwise, it will be set to a FOLLOWER state
        else:
            self.state = self.FOLLOWER
            # start the timer for the candidate
            self.candidate_timer.start()

    def suspend(self, request, context):

        p = request.period
        print(f"Command from client: suspend {str(p)}")
        print(f"SLEEPING FOR {str(p)} second{'s' if p > 1 else ''}")
        # before sleeping:
        # close (kill) all the running thread (timers)
        close_timer(self.candidate_timer)
        close_timer(self.leader_timer)
        close_timer(self.election_tracker)
        # set the sleep field to True
        self.sleep = True

        # waking up in p seconds
        wake_timer = th.Timer(p, self._wake_up)
        wake_timer.start()
        return pb2.SuspendReply()

    def getLeader(self, request, context):
        print("Command from client: getleader")
        leader_id = None

        if self.term in self.term_leaders:
            leader_id = self.term_leaders[self.term]

        if leader_id is None:
            leader_id = -1
            leader_address = ''
        else:
            leader_address = self.servers_info[leader_id]

        print(leader_id, leader_address, sep="\t")
        return pb2.GetLeaderReply(id=leader_id, address=leader_address)

    def requestVote(self, request, context):

        if self.sleep:
            return

        candidate_term = request.term
        candidate_id = request.candidateId

        # if the inequality is strict, then the candidate is qualified to be a leader
        result = candidate_term > self.term or \
                 (self.term == candidate_term and
                  (self.term not in self.term_leaders or self.term_leaders[self.term] is None))

        # print(f"RECEIVING A VOTE REQUEST FROM {str(candidate_id)} with term number:\t{str(candidate_term)}\t"
        #       f" Result: {str(result)}")
        vote_reply = pb2.VoteReply(term=max(self.term, candidate_term), result=result)

        if result:
            print(f"Voted for node {str(candidate_id)}")
            # print(f"updating term to {str(candidate_term)}")
            self.term = candidate_term
            self.term_leaders[self.term] = candidate_id
            # if the node is a current Leader: stop the leader's timer
            if self.state == self.LEADER:
                self.leader_timer.stop()
            # this will stop the candidate's vote collections
            elif self.state == self.CANDIDATE:
                self.candidate_timer.stop()
                # self.election_timer.stop()
            # set the state to FOLLOWER regardless
            self.state = self.FOLLOWER

        # if the server's current state is FOLLOWER
        #  the timer should be restarted regardless of the candidate's term number
        if self.state == self.FOLLOWER:
            self.candidate_timer.start()

        # print("state after receiving vote")
        # self._summary()
        return vote_reply

    def appendEntries(self, request, context):
        # this function will not be executed if sleep is true: it will throw an error on the receiving side
        # but this would be equivalent to unavailable behavior
        print("getting into append Entries")
        if self.sleep:
            return

        # extract the information about the heartbeat message
        heartbeat_term = request.term
        heartbeat_id = request.leader_id
        # print("#" * 30)
        # print(f"Receiving a heart beat from {str(heartbeat_id)} with term {str(heartbeat_term)}")
        # self._summary()
        # print("#" * 30)

        result = heartbeat_term >= self.term
        reply = pb2.AppendReply(term=max(heartbeat_term, self.term), result=result)

        # if the current state is LEADER:
        # this happens only when a server was a leader, was suspended, and now it is receiving heartbeats
        # from the new leader
        if self.state == self.LEADER:
            if result:
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

            if result:
                # update the term number
                self.term = heartbeat_term
                # if the leader_term is larger than the server's, update the leader's information
                self.term_leaders[self.term] = heartbeat_id

            # set the state to FOLLOWER either way
            self.state = self.FOLLOWER

            # reset the timer again
            # print("candidate timer started again!!!!")
            self.candidate_timer.start()

        # print("state after receiving heart beat")
        # self._summary()

        return reply

    def shut_down(self):
        """
        This function is created to shut down the server properly: mainly in case of keyBoard Interrupt
        :return:
        """
        close_timer(self.election_tracker)
        close_timer(self.candidate_timer)
        close_timer(self.leader_timer)
        sys.exit()

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
        print("\nShutting down")
        server.shut_down()

        sys.exit()


if __name__ == "__main__":
    args = sys.argv
    if len(args) >= 2:
        id_s = int(args[1])
        # s_term = int(args[2])
        # leader = args[3] == '1'
        main(id_s)
