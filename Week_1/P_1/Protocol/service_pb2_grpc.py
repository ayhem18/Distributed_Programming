# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import service_pb2 as service__pb2


class reverseStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ReverseString = channel.unary_unary(
                '/reverse/ReverseString',
                request_serializer=service__pb2.ReverseRequest.SerializeToString,
                response_deserializer=service__pb2.ReverseReply.FromString,
                )


class reverseServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ReverseString(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_reverseServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ReverseString': grpc.unary_unary_rpc_method_handler(
                    servicer.ReverseString,
                    request_deserializer=service__pb2.ReverseRequest.FromString,
                    response_serializer=service__pb2.ReverseReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'reverse', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class reverse(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ReverseString(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/reverse/ReverseString',
            service__pb2.ReverseRequest.SerializeToString,
            service__pb2.ReverseReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class splitStub(object):
    """the split service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.splitString = channel.unary_unary(
                '/split/splitString',
                request_serializer=service__pb2.SplitRequest.SerializeToString,
                response_deserializer=service__pb2.SplitReply.FromString,
                )


class splitServicer(object):
    """the split service
    """

    def splitString(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_splitServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'splitString': grpc.unary_unary_rpc_method_handler(
                    servicer.splitString,
                    request_deserializer=service__pb2.SplitRequest.FromString,
                    response_serializer=service__pb2.SplitReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'split', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class split(object):
    """the split service
    """

    @staticmethod
    def splitString(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/split/splitString',
            service__pb2.SplitRequest.SerializeToString,
            service__pb2.SplitReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class isPrimeStub(object):
    """the is prime service

    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.is_prime = channel.stream_stream(
                '/isPrime/is_prime',
                request_serializer=service__pb2.isPrimeRequest.SerializeToString,
                response_deserializer=service__pb2.isPrimeReply.FromString,
                )


class isPrimeServicer(object):
    """the is prime service

    """

    def is_prime(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_isPrimeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'is_prime': grpc.stream_stream_rpc_method_handler(
                    servicer.is_prime,
                    request_deserializer=service__pb2.isPrimeRequest.FromString,
                    response_serializer=service__pb2.isPrimeReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'isPrime', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class isPrime(object):
    """the is prime service

    """

    @staticmethod
    def is_prime(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/isPrime/is_prime',
            service__pb2.isPrimeRequest.SerializeToString,
            service__pb2.isPrimeReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)