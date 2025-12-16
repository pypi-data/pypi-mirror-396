from bauplan._bpln_proto.commander.service.v2 import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
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

class GetJobsRequest(_message.Message):
    __slots__ = (
        'job_ids',
        'all_users',
        'filter_users',
        'filter_kind',
        'filter_status',
        'filter_created_after',
        'filter_created_before',
        'filter_kinds',
        'filter_statuses',
        'max_records',
        'pagination_token',
    )
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    ALL_USERS_FIELD_NUMBER: _ClassVar[int]
    FILTER_USERS_FIELD_NUMBER: _ClassVar[int]
    FILTER_KIND_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUS_FIELD_NUMBER: _ClassVar[int]
    FILTER_CREATED_AFTER_FIELD_NUMBER: _ClassVar[int]
    FILTER_CREATED_BEFORE_FIELD_NUMBER: _ClassVar[int]
    FILTER_KINDS_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATUSES_FIELD_NUMBER: _ClassVar[int]
    MAX_RECORDS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    all_users: bool
    filter_users: _containers.RepeatedScalarFieldContainer[str]
    filter_kind: _common_pb2.JobKind
    filter_status: _common_pb2.JobStateType
    filter_created_after: _timestamp_pb2.Timestamp
    filter_created_before: _timestamp_pb2.Timestamp
    filter_kinds: _containers.RepeatedScalarFieldContainer[_common_pb2.JobKind]
    filter_statuses: _containers.RepeatedScalarFieldContainer[_common_pb2.JobStateType]
    max_records: int
    pagination_token: str
    def __init__(
        self,
        job_ids: _Optional[_Iterable[str]] = ...,
        all_users: bool = ...,
        filter_users: _Optional[_Iterable[str]] = ...,
        filter_kind: _Optional[_Union[_common_pb2.JobKind, str]] = ...,
        filter_status: _Optional[_Union[_common_pb2.JobStateType, str]] = ...,
        filter_created_after: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        filter_created_before: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...,
        filter_kinds: _Optional[_Iterable[_Union[_common_pb2.JobKind, str]]] = ...,
        filter_statuses: _Optional[_Iterable[_Union[_common_pb2.JobStateType, str]]] = ...,
        max_records: _Optional[int] = ...,
        pagination_token: _Optional[str] = ...,
    ) -> None: ...

class GetJobsResponse(_message.Message):
    __slots__ = ('jobs', 'pagination_token')
    JOBS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[_common_pb2.JobInfo]
    pagination_token: str
    def __init__(
        self,
        jobs: _Optional[_Iterable[_Union[_common_pb2.JobInfo, _Mapping]]] = ...,
        pagination_token: _Optional[str] = ...,
    ) -> None: ...
