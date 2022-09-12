from multiprocessing import Process
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import time


class CustomXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()


class Node(Process):
    def __init__(self, port, registry_ip, registry_port):
        super(Node, self).__init__()
        self.ft = None  # Will be defined later in the process
        self.xmlrpc_server = None

        self.port = port
        self.registry = ServerProxy(f'http://{registry_ip}:{registry_port}')
        self.id, self.registration_message = self.registry.register(port)
        if self.id == -1:
            return
        self.start()

    def get_finger_table(self):
        current_chord = self.registry.get_chord_info()
        for i in self.ft:
            # Update the finger table if it is out of date (if a node doesn't exist anymore)
            if i not in current_chord:
                self.ft = self.registry.populate_finger_table(self.id)
                break
        return self.ft

    def quit(self):
        # self.xmlrpc_server.quit = 1
        return self.registry.deregister(self.id)

    def exit_process(self):
        if self.xmlrpc_server is not None:
            self.xmlrpc_server.quit = 1

    def run(self):
        time.sleep(1)
        self.ft = self.registry.populate_finger_table(self.id)
        try:
            with CustomXMLRPCServer(('127.0.0.1', self.port), logRequests=False) as server:
                self.xmlrpc_server = server
                server.register_introspection_functions()
                server.register_function(self.get_finger_table)
                server.register_function(self.quit)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print(f"Exiting {self.name} Process ...")
                    exit(0)
                print("Exiting Node server ...")
        except:
            exit(1)
