from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class ExternalTableCreateRequest(_message.Message):
    __slots__ = ('job_request_common', 'branch_name', 'table_name', 'namespace', 'input_files', 'overwrite')
    JOB_REQUEST_COMMON_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    INPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    job_request_common: _common_pb2.JobRequestCommon
    branch_name: str
    table_name: str
    namespace: str
    input_files: SearchUris
    overwrite: bool
    def __init__(
        self,
        job_request_common: _Optional[_Union[_common_pb2.JobRequestCommon, _Mapping]] = ...,
        branch_name: _Optional[str] = ...,
        table_name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        input_files: _Optional[_Union[SearchUris, _Mapping]] = ...,
        overwrite: bool = ...,
    ) -> None: ...

class SearchUris(_message.Message):
    __slots__ = ('uris',)
    URIS_FIELD_NUMBER: _ClassVar[int]
    uris: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uris: _Optional[_Iterable[str]] = ...) -> None: ...

class ExternalTableCreateResponse(_message.Message):
    __slots__ = ('job_response_common', 'branch_name', 'table_name', 'namespace', 'user_branch_prefix')
    JOB_RESPONSE_COMMON_FIELD_NUMBER: _ClassVar[int]
    BRANCH_NAME_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    USER_BRANCH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    job_response_common: _common_pb2.JobResponseCommon
    branch_name: str
    table_name: str
    namespace: str
    user_branch_prefix: str
    def __init__(
        self,
        job_response_common: _Optional[_Union[_common_pb2.JobResponseCommon, _Mapping]] = ...,
        branch_name: _Optional[str] = ...,
        table_name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        user_branch_prefix: _Optional[str] = ...,
    ) -> None: ...
