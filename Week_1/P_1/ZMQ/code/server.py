import sys
import zmq
import helper as h

# constants for local use
CLIENT_IN = 5555
CLIENT_OUT = 5556
WORKER_IN = 8888
WORKER_OUT = 8889


def server(p1: int, p2: int, p3: int, p4: int):
    context = zmq.Context()

    # socket for user input
    c_in_socket = context.socket(zmq.REP)
    c_in_socket.bind(h.bind_string(p1))

    c_out_socket = context.socket(zmq.PUB)
    c_out_socket.bind(h.bind_string(p2))

    w_in_socket = context.socket(zmq.PUB)
    w_in_socket.bind(h.bind_string(p3))

    w_out_socket = context.socket(zmq.SUB)
    w_out_socket.bind(h.bind_string(p4))
    w_out_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        try:
            req = c_in_socket.recv_string()
            print(f"processing request: {req}")
            # send confirmation::
            c_in_socket.send_string("Message received")
            # verification string

            if h.is_valid_request(req):
                print("valid request")
                print("pass to our back servers")  # primer / gcder
                w_in_socket.send_string(req)
                print("waiting for a reply from back servers")
                try:
                    reply = w_out_socket.recv_string()
                    print(f"The servers replied with :{reply}")
                    print(f"sending the reply: {reply}")
                except zmq.ZMQError:
                    continue
                except:
                    continue
                c_out_socket.send_string(reply)

            else:
                print(f"sending this reply to the client: {req}")
                c_out_socket.send_string(req)
            # elif req:
            #     print("the request does not follow the format")
            #     print("sending back as it is")
            #     # c_out_socket.send_string(req)
            #     c_out_socket.send_string(req)
        except zmq.Again:
            pass
        except KeyboardInterrupt:
            print("\n SERVER TERMINATED !!!")
            sys.exit()


def main():
    args = sys.argv
    if len(args) == 5:  # the file name, and the two ports
        c_in = int(args[1])
        c_out = int(args[2])
        w_in = int(args[3])
        w_out = int(args[4])
        server(c_in, c_out, w_in, w_out)
    else:
        server(CLIENT_IN, CLIENT_OUT, WORKER_IN, WORKER_OUT)


if __name__ == "__main__":
    main()
