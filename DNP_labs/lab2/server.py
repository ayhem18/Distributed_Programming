import socket
from multiprocessing import Process


def quit_command():
    while True:
        cmd = input("You can enter QUIT anytime to shutdown the server.")
        if cmd == 'QUIT':
            return


class FormatError(Exception):
    pass


def calculator(cmd):
    data = cmd.split(' ')
    operator_codes = {
        '+': (lambda x, y: x+y),
        '*': (lambda x, y: x*y),
        '-': (lambda x, y: x - y),
        '/': (lambda x, y: x / y),
        '>': (lambda x, y: x > y),
        '<': (lambda x, y: x < y),
        '>=': (lambda x, y: x >= y),
        '<=': (lambda x, y: x <= y)
    }
    # if data[0] not in ['*', '+']:
    #     raise FormatError()
    return operator_codes[data[0]](float(data[1]), float(data[2]))


sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 1234))

print("Calculator server started.")
# p = Process(target=quit_command)
# p.start()

while True:
    # if not p.is_alive():
    #     break
    msg, address = sock.recvfrom(1024)
    print(f'msg from client: {msg}')
    reply = "ERROR."
    try:
        reply = str(calculator(msg.decode('utf-8')))
    except Exception as e:
        reply = "Error : " + str(e)
    sock.sendto(reply.encode('utf-8'), address)

sock.close()
print("Server shutting down.")