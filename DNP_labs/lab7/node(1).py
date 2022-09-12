import traceback
from multiprocessing import Process
from threading import Thread, Lock
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import time
import zlib


class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()


class Node(Process):
    def __init__(self, m, port, registry_ip, registry_port):
        super(Node, self).__init__()
        self.m = m
        self.ft, self.predecessor = None, None  # Will be defined later in the process
        self.xmlrpc_server = None
        self.files = {}
        self.port = port
        self.registry = ServerProxy(f'http://{registry_ip}:{registry_port}')
        self.id, self.registration_message = self.registry.register(port)
        self.ft_lock = Lock()
        self.predecessor_lock = Lock()
        self.quit_update = False
        if self.id == -1:
            return
        self.start()

    def get_finger_table(self):
        # current_chord = self.registry.get_chord_info()
        # for i in self.ft:
        #     # Update the finger table if it is out of date (if a node doesn't exist anymore)
        #     if i not in current_chord:
        #         self.ft = self.registry.populate_finger_table(self.id)
        #         break
        return self.ft

    def quit(self):
        self.quit_update = True
        res = self.registry.deregister(self.id)
        if not res[0]:
            return False, f"Node {self.id} with port {self.port} isn’t part of the network"
        succ = ServerProxy(f'http://127.0.0.1:{self.ft[str(self._successor_id())]}')
        succ.quit_notification_to_successor(self.predecessor, self.files)
        ServerProxy(f'http://127.0.0.1:{self.ft[str(self.predecessor[0])]}').quit_notification_to_predecessor()
        return res

    def exit_process(self):
        if self.xmlrpc_server is not None:
            self.xmlrpc_server.quit = 1

    def _update_finger_table(self):
        while True:
            time.sleep(1)
            if self.quit_update:
                break
            self.predecessor_lock.acquire()
            self.ft_lock.acquire()
            self.ft, self.predecessor = self.registry.populate_finger_table(self.id)
            self.predecessor_lock.release()
            self.ft_lock.release()

    def savefile(self, filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2 ** self.m

        return self.lookup(target_id, filename)


    def _successor_id(self):
        # todo: take into account the cyclical structure
        keys = list(map(int, self.ft.keys()))
        for i in range(int(self.id)+1, 2**self.m):
            if i in keys:
                return i
        return min(map(int, self.ft.keys()))

    def _farthest_node(self, target_id):
        # todo: take into account the cyclical structure
        ind = -1
        sorted_keys = sorted(map(int, self.ft.keys()))
        while sorted_keys[ind] <= target_id:
            ind += 1
            if ind == len(sorted_keys):
                break
        return sorted_keys[ind-1]
        # return max(list(filter(lambda x: x <= target_id, map(int, self.ft.keys()))))

    def lookup(self, target_id, filename):
        if int(self.predecessor[0]) < target_id <= int(self.id) or (
                int(self.predecessor[0]) > int(self.id) >= target_id):
            if self.files.get(filename):
                return False, f"{filename} already exists in Node {self.id}"
            self.files[filename] = True
            return True, f"{filename} saved in Node {self.id}"
        if int(self.id) < target_id <= int(self._successor_id()):
            print(f"Node {self.id} passed request to node {self._successor_id()}")
            successor_rpc = ServerProxy(f'http://127.0.0.1:{self.ft[str(self._successor_id())]}')
            return successor_rpc.savefile(filename)
        farthest = self._farthest_node(target_id)
        print(f"Node {self.id} passed request to node {farthest}")
        return ServerProxy(f'http://127.0.0.1:{self.ft[str(farthest)]}').savefile(filename)

    def getfile(self, filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2 ** self.m
        if int(self.predecessor[0]) < target_id <= int(self.id) or (int(self.predecessor[0]) > int(self.id) >= target_id):
            if self.files.get(filename):
                return True, f"Node {self.id} has {filename}"
            return False, f"Node {self.id} doesn’t have {filename}"
        if int(self.id) < target_id <= self._successor_id():
            print(f"Node {self.id} passed request to node {self._successor_id()}")
            successor_rpc = ServerProxy(f'http://127.0.0.1:{self.ft[str(self._successor_id())]}')
            return successor_rpc.getfile(filename)
        farthest = self._farthest_node(target_id)
        print(f"Node {self.id} passed request to node {farthest}")
        return ServerProxy(f'http://127.0.0.1:{self.ft[str(farthest)]}').getfile(filename)

    def quit_notification_to_successor(self, predecessor, files):
        self.files.update(files)
        self.predecessor_lock.acquire()
        self.predecessor = predecessor
        self.predecessor_lock.release()
        return True

    # Since the successor is taken directly from the finger table, the predecessor of a quitting node
    # can just update its finger table after the node has quit
    def quit_notification_to_predecessor(self):
        self.ft_lock.acquire()
        self.predecessor_lock.acquire()
        self.ft, self.predecessor = self.registry.populate_finger_table(self.id)
        self.predecessor_lock.release()
        self.ft_lock.release()
        return True

    def run(self):
        ft_updater = Thread(target=self._update_finger_table, daemon=True)
        ft_updater.start()
        try:
            with SimpleXMLRPCServer(('127.0.0.1', self.port), logRequests=False) as server:
                self.xmlrpc_server = server
                server.register_introspection_functions()
                server.register_function(self.get_finger_table)
                server.register_function(self.quit)
                server.register_function(self.savefile)
                server.register_function(self.getfile)
                server.register_function(self.quit_notification_to_successor)
                server.register_function(self.quit_notification_to_predecessor)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print(f"Exiting {self.name} Process ...")
                    server.server_close()
                    exit(0)
                print("Exiting Node server ...")
        except Exception as e:
            # print(e)
            # print(traceback.print_exc())
            exit(1)
