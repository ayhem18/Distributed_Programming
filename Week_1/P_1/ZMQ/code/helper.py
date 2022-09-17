def connect_string(port: int):
    return "tcp://localhost:{p}".format(p=str(port))


def bind_string(port: int):
    return "tcp://*:{p}".format(p=str(port))
