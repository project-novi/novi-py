# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from novi.proto import novi_pb2 as novi_dot_proto_dot_novi__pb2

GRPC_GENERATED_VERSION = '1.64.0'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in novi/proto/novi_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class NoviStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Login = channel.unary_unary(
                '/novi.Novi/Login',
                request_serializer=novi_dot_proto_dot_novi__pb2.LoginRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.LoginReply.FromString,
                _registered_method=True)
        self.LoginAs = channel.unary_unary(
                '/novi.Novi/LoginAs',
                request_serializer=novi_dot_proto_dot_novi__pb2.LoginAsRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.LoginAsReply.FromString,
                _registered_method=True)
        self.UseMasterKey = channel.unary_unary(
                '/novi.Novi/UseMasterKey',
                request_serializer=novi_dot_proto_dot_novi__pb2.UseMasterKeyRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.UseMasterKeyReply.FromString,
                _registered_method=True)
        self.NewSession = channel.unary_stream(
                '/novi.Novi/NewSession',
                request_serializer=novi_dot_proto_dot_novi__pb2.NewSessionRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.NewSessionReply.FromString,
                _registered_method=True)
        self.EndSession = channel.unary_unary(
                '/novi.Novi/EndSession',
                request_serializer=novi_dot_proto_dot_novi__pb2.EndSessionRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.EndSessionReply.FromString,
                _registered_method=True)
        self.CreateObject = channel.unary_unary(
                '/novi.Novi/CreateObject',
                request_serializer=novi_dot_proto_dot_novi__pb2.CreateObjectRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.CreateObjectReply.FromString,
                _registered_method=True)
        self.GetObject = channel.unary_unary(
                '/novi.Novi/GetObject',
                request_serializer=novi_dot_proto_dot_novi__pb2.GetObjectRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.GetObjectReply.FromString,
                _registered_method=True)
        self.UpdateObject = channel.unary_unary(
                '/novi.Novi/UpdateObject',
                request_serializer=novi_dot_proto_dot_novi__pb2.UpdateObjectRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.UpdateObjectReply.FromString,
                _registered_method=True)
        self.ReplaceObject = channel.unary_unary(
                '/novi.Novi/ReplaceObject',
                request_serializer=novi_dot_proto_dot_novi__pb2.ReplaceObjectRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.ReplaceObjectReply.FromString,
                _registered_method=True)
        self.DeleteObjectTags = channel.unary_unary(
                '/novi.Novi/DeleteObjectTags',
                request_serializer=novi_dot_proto_dot_novi__pb2.DeleteObjectTagsRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.DeleteObjectTagsReply.FromString,
                _registered_method=True)
        self.DeleteObject = channel.unary_unary(
                '/novi.Novi/DeleteObject',
                request_serializer=novi_dot_proto_dot_novi__pb2.DeleteObjectRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.DeleteObjectReply.FromString,
                _registered_method=True)
        self.Query = channel.unary_unary(
                '/novi.Novi/Query',
                request_serializer=novi_dot_proto_dot_novi__pb2.QueryRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.QueryReply.FromString,
                _registered_method=True)
        self.Subscribe = channel.unary_stream(
                '/novi.Novi/Subscribe',
                request_serializer=novi_dot_proto_dot_novi__pb2.SubscribeRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.SubscribeReply.FromString,
                _registered_method=True)
        self.RegisterCoreHook = channel.stream_stream(
                '/novi.Novi/RegisterCoreHook',
                request_serializer=novi_dot_proto_dot_novi__pb2.RegCoreHookRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.RegCoreHookReply.FromString,
                _registered_method=True)
        self.RegisterFunction = channel.stream_stream(
                '/novi.Novi/RegisterFunction',
                request_serializer=novi_dot_proto_dot_novi__pb2.RegFunctionRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.RegFunctionReply.FromString,
                _registered_method=True)
        self.CallFunction = channel.unary_unary(
                '/novi.Novi/CallFunction',
                request_serializer=novi_dot_proto_dot_novi__pb2.CallFunctionRequest.SerializeToString,
                response_deserializer=novi_dot_proto_dot_novi__pb2.CallFunctionReply.FromString,
                _registered_method=True)


class NoviServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LoginAs(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UseMasterKey(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def NewSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def EndSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReplaceObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteObjectTags(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteObject(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterCoreHook(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterFunction(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CallFunction(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NoviServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.LoginRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.LoginReply.SerializeToString,
            ),
            'LoginAs': grpc.unary_unary_rpc_method_handler(
                    servicer.LoginAs,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.LoginAsRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.LoginAsReply.SerializeToString,
            ),
            'UseMasterKey': grpc.unary_unary_rpc_method_handler(
                    servicer.UseMasterKey,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.UseMasterKeyRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.UseMasterKeyReply.SerializeToString,
            ),
            'NewSession': grpc.unary_stream_rpc_method_handler(
                    servicer.NewSession,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.NewSessionRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.NewSessionReply.SerializeToString,
            ),
            'EndSession': grpc.unary_unary_rpc_method_handler(
                    servicer.EndSession,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.EndSessionRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.EndSessionReply.SerializeToString,
            ),
            'CreateObject': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateObject,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.CreateObjectRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.CreateObjectReply.SerializeToString,
            ),
            'GetObject': grpc.unary_unary_rpc_method_handler(
                    servicer.GetObject,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.GetObjectRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.GetObjectReply.SerializeToString,
            ),
            'UpdateObject': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateObject,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.UpdateObjectRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.UpdateObjectReply.SerializeToString,
            ),
            'ReplaceObject': grpc.unary_unary_rpc_method_handler(
                    servicer.ReplaceObject,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.ReplaceObjectRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.ReplaceObjectReply.SerializeToString,
            ),
            'DeleteObjectTags': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteObjectTags,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.DeleteObjectTagsRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.DeleteObjectTagsReply.SerializeToString,
            ),
            'DeleteObject': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteObject,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.DeleteObjectRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.DeleteObjectReply.SerializeToString,
            ),
            'Query': grpc.unary_unary_rpc_method_handler(
                    servicer.Query,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.QueryRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.QueryReply.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.SubscribeRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.SubscribeReply.SerializeToString,
            ),
            'RegisterCoreHook': grpc.stream_stream_rpc_method_handler(
                    servicer.RegisterCoreHook,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.RegCoreHookRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.RegCoreHookReply.SerializeToString,
            ),
            'RegisterFunction': grpc.stream_stream_rpc_method_handler(
                    servicer.RegisterFunction,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.RegFunctionRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.RegFunctionReply.SerializeToString,
            ),
            'CallFunction': grpc.unary_unary_rpc_method_handler(
                    servicer.CallFunction,
                    request_deserializer=novi_dot_proto_dot_novi__pb2.CallFunctionRequest.FromString,
                    response_serializer=novi_dot_proto_dot_novi__pb2.CallFunctionReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'novi.Novi', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('novi.Novi', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Novi(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/Login',
            novi_dot_proto_dot_novi__pb2.LoginRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.LoginReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def LoginAs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/LoginAs',
            novi_dot_proto_dot_novi__pb2.LoginAsRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.LoginAsReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UseMasterKey(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/UseMasterKey',
            novi_dot_proto_dot_novi__pb2.UseMasterKeyRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.UseMasterKeyReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def NewSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/novi.Novi/NewSession',
            novi_dot_proto_dot_novi__pb2.NewSessionRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.NewSessionReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def EndSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/EndSession',
            novi_dot_proto_dot_novi__pb2.EndSessionRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.EndSessionReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CreateObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/CreateObject',
            novi_dot_proto_dot_novi__pb2.CreateObjectRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.CreateObjectReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/GetObject',
            novi_dot_proto_dot_novi__pb2.GetObjectRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.GetObjectReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/UpdateObject',
            novi_dot_proto_dot_novi__pb2.UpdateObjectRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.UpdateObjectReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ReplaceObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/ReplaceObject',
            novi_dot_proto_dot_novi__pb2.ReplaceObjectRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.ReplaceObjectReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteObjectTags(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/DeleteObjectTags',
            novi_dot_proto_dot_novi__pb2.DeleteObjectTagsRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.DeleteObjectTagsReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteObject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/DeleteObject',
            novi_dot_proto_dot_novi__pb2.DeleteObjectRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.DeleteObjectReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Query(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/Query',
            novi_dot_proto_dot_novi__pb2.QueryRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.QueryReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(
            request,
            target,
            '/novi.Novi/Subscribe',
            novi_dot_proto_dot_novi__pb2.SubscribeRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.SubscribeReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RegisterCoreHook(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/novi.Novi/RegisterCoreHook',
            novi_dot_proto_dot_novi__pb2.RegCoreHookRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.RegCoreHookReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RegisterFunction(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(
            request_iterator,
            target,
            '/novi.Novi/RegisterFunction',
            novi_dot_proto_dot_novi__pb2.RegFunctionRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.RegFunctionReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CallFunction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/novi.Novi/CallFunction',
            novi_dot_proto_dot_novi__pb2.CallFunctionRequest.SerializeToString,
            novi_dot_proto_dot_novi__pb2.CallFunctionReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
