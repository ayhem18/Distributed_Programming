# this file is created of checking the semantics of the protocol used in this simple file transfer application
# It used mainly to verify whether the message sent by hosts respect the criteria set by the protocol

# global variables for safer string comparison

start_code = 's'
data_code = 'd'
delimiter = " | "
ack_code = 'a'
ENCODE = 'UTF-8'


def verify_ack_start(data_received: bytes):
    """this function is used to verify whether the acknowledgement message
    sent by the server respects the pattern set by the protocol
    it will return a list of the main components of the message if it is valid
    and None otherwise
    """

    data_str = get_str(data_received)
    comps = data_str.split(delimiter)
    if len(comps) < 3:
        return None

    verify = comps[0] == ack_code and comps[1].isdigit() and comps[2].isdigit()
    return comps[:3] if verify else None


def verify_ack_data(data_received: bytes):
    """this function verifies whether the Acknowledgement message 
    sent by the server succeeding a data message follows the protocol or not
    If the message is valid, it will return the main components.
    Otherwise, it will return None"""

    data_str = get_str(data_received)
    comps = data_str.split(delimiter)

    if len(comps) < 2:
        return None

    verify = comps[0] == ack_code and comps[1].isdigit()

    return comps[:2] if verify else None


def verify_start_msg(data_received: bytes):
    # the data passed might contain data that cannot be de/encoded with utf-8
    try:
        data_str = get_str(data_received)
        comps = data_str.split(delimiter)
    except:
        return None

    if len(comps) < 4:
        return None
    verify = (comps[0] == start_code and comps[1].isdigit() and comps[3].isdigit())
    return comps[:4] if verify else None


def verify_data_msg(data_received):
    try:
        prefix, rest = data_received.split(delimiter.encode(), 1)
        seq_num, data_bytes = rest.split(delimiter.encode(), 1)
        verify = (get_str(prefix) == data_code and get_str(seq_num).isdigit())

        prefix = prefix.decode()
        return [prefix, seq_num, data_bytes] if verify else None
    except:
        return None


def data_msg_header_size(seq_num: int):
    return len(data_code + delimiter + str(seq_num) + delimiter)


def get_str(string):
    return string if isinstance(string, str) else string.decode(ENCODE)


def get_bytes(string):
    try:
        return bytes(string)
    except:
        try:
            return string.encode(ENCODE)
        except UnicodeError:
            return string

