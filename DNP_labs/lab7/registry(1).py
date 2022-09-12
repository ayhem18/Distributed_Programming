from multiprocessing import Process
from xmlrpc.server import SimpleXMLRPCServer
import random
import bisect


class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()


def _successor(id, sorted_ids):
    try:
        return sorted_ids[bisect.bisect_left(sorted_ids, id)]
    except IndexError:
        return sorted_ids[0]

def _predecessor(id, sorted_ids):
    try:
        return sorted_ids[bisect.bisect_left(sorted_ids, id)-1]
    except IndexError:
        return sorted_ids[-1]


class Registry(Process):
    def __init__(self, m, ip, port):
        super(Registry, self).__init__()
        self.ports = {}
        self.m = m
        self.ip = ip
        self.port = port
        self.xmlrpc_server = None
        self.start()

    def register(self, port):
        if len(self.ports) == 2 ** self.m:
            return -1, "Chord is full."
        id = str(random.randint(0, 2 ** self.m - 1))
        while id in self.ports:
            id = str(random.randint(0, 2 ** self.m - 1))
        self.ports[str(id)] = port
        return id, f"New chord size : {len(self.ports)}"

    def deregister(self, id):
        id = str(id)
        if self.ports.get(id) is None:
            return False, f"Node {id} isn’t part of the network"
        port = self.ports[id]
        self.ports.pop(str(id), None)
        return True, f"Node {id}  with  port  {port}  was successfully removed"

    def get_chord_info(self):
        return self.ports

    def populate_finger_table(self, id):
        id = str(id)
        ft = {}
        sorted_ids = sorted(map(int, self.ports.keys()))
        for i in range(1, self.m + 1):
            succ = _successor((int(id) + 2 ** (i - 1)) % 2 ** self.m, sorted_ids)
            ft[str(succ)] = self.ports[str(succ)]
        pred = str(_predecessor(int(id), sorted_ids))
        return ft, (pred, self.ports[pred])

    def exit_process(self):
        if self.xmlrpc_server is not None:
            self.xmlrpc_server.quit = 1

    def run(self):
        random.seed(0)
        try:
            with CustomXMLRPCServer((self.ip, self.port), logRequests=False) as server:
                self.xmlrpc_server = server
                server.register_introspection_functions()
                server.register_function(self.register)
                server.register_function(self.deregister)
                server.register_function(self.get_chord_info)
                server.register_function(self.populate_finger_table)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("Exiting Registry Process ...")
                    exit(0)
        except Exception as e:
            exit(1)
