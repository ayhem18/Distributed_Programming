import sys

import queue_pb2_grpc as pb2_grpc
import queue_pb2 as pb2
import grpc
from concurrent import futures
import re

class Server(pb2_grpc.queueServicer):

    def __init__(self, port: int, max_size: int):
        self.address = f"127.0.0.1:{str(port)}"
        self.max_size = max_size
        self.queue = []

    def PutItem(self, request, context):
        if len(self.queue) == self.max_size:
            return pb2.R