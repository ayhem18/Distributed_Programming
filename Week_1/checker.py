# this file is created of checking the semantics of the protocol used in this simple file transfer application
# It used mainly to verify whether the message sent by hosts respect the criteria set by the protocol

import socket

## global variables for safer string comparison

start_code = 's'
data_code = 'd'
delimiter = "|"
ack_code = 'a'


def verify_ack_start(data_received: bytes):
    
    """this function is used to verify whether the acknowledgement message
    sent by the server respects the pattern set by the protocol
    it will return a list of the main components of the message if it is valid
    and None otherwise
    """
    
    data_str = data_received.decode()
    comps = data_str.split(delimiter)
    if len(comps) < 3: 
        return None
    
    try:
        verify =  comps[0] == ack_code and comps[1].isdigit() and comps[2].isdigit()
    except:
        verify = False
    return comps[:3] if verify else None


def verify_data_start(data_received: bytes):
    """this function verifies whether the Acknowledgement message 
    sent by the server succeeding a data message follows the protocol or not
    If the message is valid, it will return the main components.
    Otherwise, it will return None"""
    
    data_str = data_received.decode()
    comps = data_str.split(delimiter)
    
    if len(comps) < 2 : 
        return None
    
    verify = False
    try:
        verify =  comps[0] == ack_code and comps[1].isdigit() 
    except:
        verify = False
    return comps[:2] if verify else None

    