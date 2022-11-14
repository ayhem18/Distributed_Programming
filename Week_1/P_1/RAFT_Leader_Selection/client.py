import re
import sys

import grpc

import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc

QUIT = 'quit'
CLIENT_TERMINATING = "CLIENT TERMINATING"
PROMPT_INPUT = "\nPlease enter a command\n"


def suspend_command(text: str):
    suspend_pattern = r"suspend(\s)+(\d+)"
    match = re.fullmatch(suspend_pattern, text)
    if match:
        suspend_time = int(re.split(r"\s+", text)[1])
        return suspend_time
    return None


def connect_command(text: str):
    connect_pattern = r"connect(\s)+(\d+\.)*(\d)+(\s)+(\d)+"
    match = re.fullmatch(connect_pattern, text)
    if match is not None:
        addr, port = re.split(r"\s+", text)[1:]
        return addr + ":" + port
    return None


def main():
    channel = None
    client = None
    try:
        while True:
            last_valid_address = None
            user_input = input(PROMPT_INPUT).strip().lower()
            server_addr = connect_command(user_input)
            suspend_time = suspend_command(user_input)
            if server_addr is not None:
                last_valid_address = server_addr
                print(f"Client connected to {server_addr}")
                channel = grpc.insecure_channel(server_addr)
                # set the reverse service
                client = pb2_grpc.serverStub(channel)

            elif user_input == QUIT:
                print("CLIENT QUITTING")
                sys.exit()

            elif user_input == 'getleader':

                if channel is None:
                    print("CLIENT IS CURRENTLY NOT CONNECTED TO ANY SERVER\nPLEASE CONNECT FIRST")
                    continue

                get_leader_request = pb2.GetLeaderRequest()
                get_leader_reply = client.getLeader(get_leader_request)
                leader_id, leader_addr = get_leader_reply.id, get_leader_reply.address

                if len(leader_addr) != 0:
                    print(f"Current leader:\t id:{str(leader_id)}, address:{leader_addr}")
                else:
                    print("NO current leader")
            elif suspend_time:

                if channel is None:
                    print("CLIENT IS CURRENTLY NOT CONNECTED TO ANY SERVER\nPLEASE CONNECT FIRST")
                    continue
                suspend_request = pb2.SuspendRequest(period=suspend_time)
                client.suspend(suspend_request)
            else:
                print("DEAR USER PLEASE MAKE SURE TO FORMAT YOUR INPUT CORRECTLY...")

    except KeyboardInterrupt:
        print(CLIENT_TERMINATING)


if __name__ == "__main__":
    main()
