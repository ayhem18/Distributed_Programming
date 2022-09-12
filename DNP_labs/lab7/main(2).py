import sys
import time
import traceback
import zlib
from xmlrpc.client import ServerProxy

from registry import Registry
from node import Node


registry_ip = '127.0.0.1'

m = 5
first_port = 0
last_port = 0

if len(sys.argv) == 3:
    first_port = int(sys.argv[1])
    last_port = int(sys.argv[2])
elif len(sys.argv) == 4:
    m = int(sys.argv[1])
    first_port = int(sys.argv[2])
    last_port = int(sys.argv[3])
else:
    print("ERROR: Invalid arguments.")
    exit(1)

registry_port = last_port + 1


reg = None
attempts = 5
while reg is None:
    reg = Registry(m, registry_ip, registry_port)
    attempts -= 1
    time.sleep(0.2)
    if not reg.is_alive():
        reg = None
        registry_port += 1
    if not attempts:
        print("Failed to find a port for the Registry XMLRPC Server after 5 attempts.\nExiting ...")
        exit(1)

registry_server = ServerProxy(f'http://{registry_ip}:{registry_port}')


nodes = [Node(m, i, registry_ip, registry_port) for i in range(first_port, last_port + 1)]

time.sleep(1)

for i in nodes:
    if not i.is_alive():
        if i.id == -1:
            print(f"Couldn't start node on port {i.port} ({i.registration_message})\nExiting ...")
        else:  # Node didn't start for another reason (Probably the port is not available)
            print(f"Couldn't start node on port {i.port}.\nExiting ...")
        for x in nodes:
            try:
                x.kill()
            except Exception as e:
                pass
        reg.kill()
        exit(1)

time.sleep(0.5)

node_servers = {}

for i in range(first_port, last_port + 1):
    node_server = ServerProxy(f'http://127.0.0.1:{i}')
    node_servers[str(i)] = node_server

print(f"Registry and {last_port-first_port+1} nodes are created. ")
while True:
    try:
        cmd = input("> ").split()
        if cmd[0] == 'get_chord_info':
            print(eval(f"registry_server.{cmd[0]}({','.join(cmd[1:])})"))
        elif cmd[0] == 'get_finger_table':
            print(eval(f"node_servers['{cmd[1]}'].{cmd[0]}({','.join(cmd[2:])})"))
        elif cmd[0] == 'quit':
            if cmd[1] not in node_servers:
                print(f"Node with port {cmd[1]} isn’t available")
            print(node_servers[cmd[1]].quit())

        elif cmd[0] == 'save':
            hash_value = zlib.adler32(cmd[2].encode())
            target_id = hash_value % 2 ** m
            print(f"{cmd[2]} has identifier {target_id}")
            print(node_servers[cmd[1]].savefile(cmd[2]))
        elif cmd[0] == 'get':
            hash_value = zlib.adler32(cmd[2].encode())
            target_id = hash_value % 2 ** m
            print(f"{cmd[2]} has identifier {target_id}")
            print(node_servers[cmd[1]].getfile(cmd[2]))
        else:
            print("Invalid command.")
    except KeyboardInterrupt:
        reg.join()
        for i in nodes:
            i.join()
        print("Exiting Main Process...")
        exit(0)
    except Exception as e:
        # print(traceback.format_exc())
        print(f"Invalid command ({e})")
        # print(e.with_traceback())
