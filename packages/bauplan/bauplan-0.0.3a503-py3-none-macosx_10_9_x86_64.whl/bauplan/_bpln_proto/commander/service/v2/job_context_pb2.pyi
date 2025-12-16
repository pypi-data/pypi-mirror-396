from bauplan._bpln_proto.commander.service.v2 import runner_events_pb2 as _runner_events_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
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

class BauplanRef(_message.Message):
    __slots__ = ('name', 'hash')
    class RefType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REF_TYPE_UNSPECIFIED: _ClassVar[BauplanRef.RefType]
        REF_TYPE_COMMIT: _ClassVar[BauplanRef.RefType]
        REF_TYPE_BRANCH: _ClassVar[BauplanRef.RefType]
        REF_TYPE_TRANSACTION_BRANCH: _ClassVar[BauplanRef.RefType]

    REF_TYPE_UNSPECIFIED: BauplanRef.RefType
    REF_TYPE_COMMIT: BauplanRef.RefType
    REF_TYPE_BRANCH: BauplanRef.RefType
    REF_TYPE_TRANSACTION_BRANCH: BauplanRef.RefType
    NAME_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    name: str
    hash: str
    def __init__(self, name: _Optional[str] = ..., hash: _Optional[str] = ...) -> None: ...

class ModelNode(_message.Message):
    __slots__ = ('model_id', 'model_name')
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    model_id: str
    model_name: str
    def __init__(self, model_id: _Optional[str] = ..., model_name: _Optional[str] = ...) -> None: ...

class ModelEdge(_message.Message):
    __slots__ = ('source_id', 'destination_id')
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_ID_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    destination_id: str
    def __init__(self, source_id: _Optional[str] = ..., destination_id: _Optional[str] = ...) -> None: ...

class JobContext(_message.Message):
    __slots__ = (
        'job_id',
        'project_id',
        'project_name',
        'ref',
        'branch',
        'transaction_branch',
        'code_snapshot',
        'models',
        'model_deps',
        'job_events',
    )
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    BRANCH_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_BRANCH_FIELD_NUMBER: _ClassVar[int]
    CODE_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    MODELS_FIELD_NUMBER: _ClassVar[int]
    MODEL_DEPS_FIELD_NUMBER: _ClassVar[int]
    JOB_EVENTS_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    project_id: str
    project_name: str
    ref: str
    branch: str
    transaction_branch: BauplanRef
    code_snapshot: bytes
    models: _containers.RepeatedCompositeFieldContainer[ModelNode]
    model_deps: _containers.RepeatedCompositeFieldContainer[ModelEdge]
    job_events: _containers.RepeatedCompositeFieldContainer[_runner_events_pb2.RunnerEvent]
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        project_id: _Optional[str] = ...,
        project_name: _Optional[str] = ...,
        ref: _Optional[str] = ...,
        branch: _Optional[str] = ...,
        transaction_branch: _Optional[_Union[BauplanRef, _Mapping]] = ...,
        code_snapshot: _Optional[bytes] = ...,
        models: _Optional[_Iterable[_Union[ModelNode, _Mapping]]] = ...,
        model_deps: _Optional[_Iterable[_Union[ModelEdge, _Mapping]]] = ...,
        job_events: _Optional[_Iterable[_Union[_runner_events_pb2.RunnerEvent, _Mapping]]] = ...,
    ) -> None: ...

class JobError(_message.Message):
    __slots__ = ('job_id', 'error_msg', 'error_code', 'error_type')
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    error_msg: str
    error_code: int
    error_type: str
    def __init__(
        self,
        job_id: _Optional[str] = ...,
        error_msg: _Optional[str] = ...,
        error_code: _Optional[int] = ...,
        error_type: _Optional[str] = ...,
    ) -> None: ...

class GetJobContextRequest(_message.Message):
    __slots__ = ('job_ids', 'start', 'end', 'limit', 'include_logs', 'include_snapshot')
    JOB_IDS_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_LOGS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    job_ids: _containers.RepeatedScalarFieldContainer[str]
    start: int
    end: int
    limit: int
    include_logs: bool
    include_snapshot: bool
    def __init__(
        self,
        job_ids: _Optional[_Iterable[str]] = ...,
        start: _Optional[int] = ...,
        end: _Optional[int] = ...,
        limit: _Optional[int] = ...,
        include_logs: bool = ...,
        include_snapshot: bool = ...,
    ) -> None: ...

class GetJobContextResponse(_message.Message):
    __slots__ = ('job_contexts', 'errors')
    JOB_CONTEXTS_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    job_contexts: _containers.RepeatedCompositeFieldContainer[JobContext]
    errors: _containers.RepeatedCompositeFieldContainer[JobError]
    def __init__(
        self,
        job_contexts: _Optional[_Iterable[_Union[JobContext, _Mapping]]] = ...,
        errors: _Optional[_Iterable[_Union[JobError, _Mapping]]] = ...,
    ) -> None: ...
