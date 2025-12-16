from __future__ import annotations

import io
import re
import shutil
import sys
import warnings
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from google import protobuf
from pydantic import BaseModel, Field, PrivateAttr

from ._bpln_proto.commander.service.v2 import common_pb2 as common_pb
from ._bpln_proto.commander.service.v2 import get_jobs_pb2 as get_jobs_pb
from ._bpln_proto.commander.service.v2 import get_logs_pb2 as get_logs_pb
from ._bpln_proto.commander.service.v2 import job_context_pb2 as job_context_pb
from ._bpln_proto.commander.service.v2 import runner_events_pb2 as runner_events_pb

T = TypeVar('T')
RT = TypeVar('RT')
PageT = TypeVar('PageT')

# TODO: this alias is for backwards compatibility, but I would like to remove it
JobLog: TypeAlias = 'JobLogEvent'
DateRange: TypeAlias = tuple[Optional[datetime], Optional[datetime]]


REF_REGEX = r'^(.*?)(:?@([^@]+))?$'

HOME_DIRPATH = Path.home()


# Safely convert proto timestamp fields to native Python datetime
def proto_datetime_to_py_datetime(
    ts: protobuf.timestamp_pb2.Timestamp,
) -> Optional[datetime]:
    if not ts.seconds and not ts.nanos:
        return None
    return ts.ToDatetime()


class _BauplanData(BaseModel):
    def __str__(self) -> str:
        return self.__repr__()


class Ref(_BauplanData):
    """A branch or a tag

    ## Examples:
    ```python
    ref = Ref(name='main', hash='abc123')
    ```

    Attributes:
        name (str): The name of the branch or tag.
        hash (Optional[str]): The hash of the branch or tag. This is optional and may be None.
        type (Optional[str]): The type of the ref, either 'BRANCH', 'TAG', or 'DETACHED'.
    """

    name: str
    hash: str | None = None
    type: str | None = None

    def __str__(self) -> str:
        if self.hash:
            return f'{self.name}@{self.hash}'
        return self.name

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        return cls(**data)

    @classmethod
    def from_string(cls, ref: str) -> Self:
        matched = re.match(REF_REGEX, ref)
        if not matched:
            raise ValueError(f'invalid ref format: {ref}')
        name = matched.group(1).strip()
        hash = matched.group(3) or None
        if not name:
            raise ValueError(f'invalid ref format: {ref}')
        return cls(name=name, hash=hash)


class Branch(Ref):
    type: Literal['BRANCH'] = 'BRANCH'


class Tag(Ref):
    type: Literal['TAG'] = 'TAG'


class DetachedRef(Ref):
    type: Literal['DETACHED'] = 'DETACHED'


class DAGNode(_BauplanData):
    """A bauplan function that produces a Model.

    Attributes:
        id: The model ID
        name: The model name
    """

    id: str
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)


class DAGEdge(_BauplanData):
    """A dependency between DAGNode instances, representing dataflow."""

    source_model: Optional[str]
    destination_model: str

    @property
    def is_scan(self) -> bool:
        return self.source_model is None


APIRef: TypeAlias = Annotated[
    Union[Branch, Tag, DetachedRef],
    Field(discriminator='type'),
]


class APIMetadata(_BauplanData):
    status_code: int
    ref: Optional[APIRef] = None
    username: Optional[str] = None
    error: Optional[str] = None
    pagination_token: Optional[str] = None
    request_id: str
    request_ts: int
    request_ms: int


class APIError(_BauplanData):
    code: int
    type: str
    message: str
    context: dict[str, Any]


class APIResponse(_BauplanData):
    metadata: APIMetadata
    ref: Optional[APIRef] = None


class APIResponseWithData(APIResponse):
    data: Any
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class APIResponseWithError(APIResponse):
    error: APIError
    ref: Optional[APIRef] = None
    metadata: APIMetadata


class Namespace(_BauplanData):
    name: str
    ref: Optional[APIRef] = None


class EntryType(str, Enum):
    TABLE = 'TABLE'
    EXTERNAL_TABLE = 'EXTERNAL_TABLE'


class Entry(_BauplanData):
    name: str
    namespace: str
    kind: EntryType

    @property
    def fqn(self) -> str:
        return f'{self.namespace}.{self.name}'


class TableField(_BauplanData):
    id: int
    name: str
    required: bool
    type: str


class PartitionField(_BauplanData):
    name: str
    transform: str


class Table(Entry):
    kind: EntryType = EntryType.TABLE

    def is_managed(self) -> bool:
        return self.kind == EntryType.TABLE

    def is_external(self) -> bool:
        return self.kind == EntryType.EXTERNAL_TABLE


class TableWithMetadata(Table):
    id: str
    records: Optional[int]
    size: Optional[int]
    last_updated_ms: int
    fields: List[TableField]
    snapshots: Optional[int]
    partitions: List[PartitionField]
    metadata_location: str
    current_snapshot_id: Optional[int]
    current_schema_id: Optional[int]
    properties: Optional[Dict[str, str]]
    raw: Optional[Dict]


class Commit(_BauplanData):
    """
    A commit is a record of a change in the data lake.

    Attributes:
        ref (APIRef): The reference (branch or tag) associated with the commit.
        message (Optional[str]): The commit message.
        authors (List[Actor]): A list of authors associated with the commit.
        authored_date (datetime): The date and time when the commit was authored.
        committer (Actor): The committer of the commit.
        committed_date (datetime): The date and time when the commit was committed.
        parent_ref (APIRef): The reference to the parent commit.
        parent_hashes (List[str]): A list of parent commit hashes.
        properties (Dict[str, str]): A dictionary of properties associated with the commit.
        signed_off_by (List[Actor]): A list of actors who signed off on the commit.
    """

    ref: APIRef
    message: Optional[str]
    authors: List[Actor]
    authored_date: datetime
    committer: Actor
    committed_date: datetime
    parent_ref: APIRef
    parent_hashes: List[str]
    properties: Dict[str, str]
    signed_off_by: List[Actor]

    @property
    def author(self) -> Actor:
        return self.authors[0]

    @property
    def subject(self) -> Optional[str]:
        if self.message is None:
            return None
        subject = self.message.strip().split('\n')[0].strip()
        return subject or None

    @property
    def body(self) -> Optional[str]:
        if self.message is None:
            return None
        body = '\n'.join(self.message.strip().split('\n')[1:]).strip()
        return body or None

    @property
    def parent_merge_ref(self) -> Optional[Branch]:
        if len(self.parent_hashes) > 1:
            return Branch(name=self.parent_ref.name, hash=self.parent_hashes[1])
        return None


class Actor(_BauplanData):
    name: str
    email: str | None


@dataclass
class _BauplanIteratorContext:
    page_idx: int = 0
    page_item_idx: int = 0
    idx: int = 0
    finished: bool = False

    def next_page(self) -> None:
        self.page_idx = self.page_idx + 1
        self.page_item_idx = 0

    def next_item(self, limit: int | None) -> None:
        self.page_item_idx = self.page_item_idx + 1
        self.idx = self.idx + 1
        self.finished = True if limit and self.idx >= limit else False


class _BauplanIterableResponse(ABC, Generic[T, RT, PageT]):
    """Abstract base class for paginated iterable responses.

    This class provides the common pagination logic for both HTTP API responses
    and RPC/gRPC responses. Subclasses must implement the abstract methods to
    extract items and pagination tokens from their specific response types.

    Type Parameters:
        T: The type of items returned by the iterator (e.g., Job, Branch)
        RT: The type of the ref associated with the response (e.g., Branch, Tag, or None)
        PageT: The type of each page response (e.g., APIResponse, GetJobsResponse)
    """

    responses: List[PageT]

    def __init__(
        self,
        data_fetcher: Callable[[int, Optional[str]], PageT],
        data_mapper: Callable[[Any], T],
        itersize: int,
        limit: int | None = None,
    ) -> None:
        self.responses = []

        self._response_ref: RT = None  # type: ignore
        self._limit = limit
        self._itersize = itersize
        self._data_fetcher = data_fetcher
        self._data_mapper = data_mapper
        self._iter = _BauplanIteratorContext()
        self._has_next_page = True
        self._fetch_next_page()

    # Abstract methods to be implemented by subclasses

    @abstractmethod
    def _get_page_items(self, page: PageT) -> Sequence[Any]:
        """Extract the list of raw items from a page response."""
        ...

    @abstractmethod
    def _get_pagination_token(self, page: PageT) -> Optional[str]:
        """Extract the pagination token from a page response."""
        ...

    def _get_page_ref(self, page: PageT) -> Optional[RT]:
        """Extract the ref from a page response. Override in subclasses if needed."""
        return None

    # Common implementation

    def values(self) -> List[T]:
        return list(self)

    def __iter__(self) -> _BauplanIterableResponse[T, RT, PageT]:
        # We need to reset the iterator context
        self._iter = _BauplanIteratorContext()
        return self

    def __getitem__(self, idx: int) -> T:
        if idx < 0:
            raise ValueError('Negative indexing is not supported')
        # TODO: this is not efficient
        pos = 0
        for res in self:
            if pos == idx:
                return res
            pos += 1
        raise IndexError('Index out of range')

    def __next__(self) -> T:
        if self._iter.finished:
            raise StopIteration
        # Get the current page
        page = self.responses[self._iter.page_idx]
        page_items = self._get_page_items(page)
        if self._iter.page_item_idx >= len(page_items):
            # We've reached the end of the current page
            self._fetch_next_page()
            self._iter.next_page()
            self._iter.finished = self._iter.page_idx >= len(self.responses)
            return self.__next__()
        # Get the current item
        item = page_items[self._iter.page_item_idx]
        self._iter.next_item(self._limit)
        return self._data_mapper(item)

    def __len__(self) -> int:
        while self._has_next_page:
            self._fetch_next_page()
        return self._response_data_len()

    def __str__(self) -> str:
        ref = '' if not hasattr(self, 'ref') else f'ref={str(self.ref)!r}, '
        return f'{self.__class__.__name__}({ref}count={len(self.responses)})'

    def _response_data_len(self) -> int:
        # Actual number of items fetched over all pages
        return sum(len(self._get_page_items(page)) for page in self.responses)

    @property
    def _next_pagination_token(self) -> Optional[str]:
        if not self._has_next_page:
            return None
        if self.responses:
            return self._get_pagination_token(self.responses[-1])
        return None

    def _fetch_next_page(self) -> None:
        if not self._has_next_page:
            return
        if self._limit:
            # We should fetch only the remaining items, without exceeding the setted itersize
            missing_items = min(self._itersize, self._limit - self._response_data_len())
        else:
            # Without an explicit limit, we should fetch the itersize
            missing_items = self._itersize
        page = self._data_fetcher(missing_items, self._next_pagination_token)
        self.responses.append(page)
        page_ref = self._get_page_ref(page)
        if page_ref and not self._response_ref:
            self._response_ref = cast(RT, page_ref)
        # We need to use the private __len method to prevent an infinite loop
        tot_items = self._response_data_len()
        if self._limit and tot_items >= self._limit:
            # We should stop fetching pages when we have enough items
            self._has_next_page = False
        else:
            # We should stop fetching pages when there are no more pages
            self._has_next_page = self._next_pagination_token is not None


class _BauplanIterableCatalogAPIResponse(_BauplanIterableResponse[T, RT, APIResponse]):
    """Iterable response for HTTP Catalog API calls."""

    def __init__(
        self,
        data_fetcher: Callable[[int, Optional[str]], APIResponse],
        data_mapper: Callable[[Dict[str, Any]], T],
        itersize: int,
        limit: int | None = None,
    ) -> None:
        super().__init__(data_fetcher, data_mapper, itersize, limit)

    def _get_page_items(self, page: APIResponse) -> Sequence[Any]:
        return page.data

    def _get_pagination_token(self, page: APIResponse) -> Optional[str]:
        return page.metadata.pagination_token

    def _get_page_ref(self, page: APIResponse) -> Optional[RT]:
        return cast(RT, page.ref) if page.ref else None

    def __str__(self) -> str:
        ref = '' if not hasattr(self, 'ref') else f'ref={str(self.ref)!r}, '
        return f'{self.__class__.__name__}({ref}iterator={self.responses[0].metadata.request_id!r})'


class _BauplanIterableRPCResponse(_BauplanIterableResponse[T, RT, PageT]):
    """Iterable response for RPC/gRPC calls.

    This class uses callable extractors to handle the varying structure of
    protobuf response messages.

    Type Parameters:
        T: The type of items returned by the iterator (e.g., Job)
        RT: The type of the ref associated with the response (usually None for RPC)
        PageT: The type of the protobuf response message (e.g., GetJobsResponse)
    """

    def __init__(
        self,
        data_fetcher: Callable[[int, Optional[str]], PageT],
        data_mapper: Callable[[Any], T],
        items_extractor: Callable[[PageT], Sequence[Any]],
        token_extractor: Callable[[PageT], Optional[str]],
        itersize: int,
        limit: int | None = None,
    ) -> None:
        self._items_extractor = items_extractor
        self._token_extractor = token_extractor
        super().__init__(data_fetcher, data_mapper, itersize, limit)

    def _get_page_items(self, page: PageT) -> Sequence[Any]:
        return self._items_extractor(page)

    def _get_pagination_token(self, page: PageT) -> Optional[str]:
        return self._token_extractor(page)


class _BauplanIterableCatalogAPIResponseWithRef(_BauplanIterableCatalogAPIResponse[T, RT]):
    @property
    def ref(self) -> RT:
        return self._response_ref


class GetCommitsResponse(_BauplanIterableCatalogAPIResponseWithRef[Commit, Union[Branch, Tag]]):
    """
    An Iterable containing `bauplan.schema.Commit` objects returned by `get_commits` method.
    """

    ...


class GetTablesResponse(_BauplanIterableCatalogAPIResponseWithRef[TableWithMetadata, Union[Branch, Tag]]):
    """
    An Iterable containing `bauplan.schema.TableWithMetadata` objects returned by `get_tables` method.

    ## Example:
    ```python notest
    response = client.get_tables(namespace='my_namespace', ref='main')
    for table in response:
        print(table.name, table.records)
    ```
    """

    ...


class GetNamespacesResponse(_BauplanIterableCatalogAPIResponseWithRef[Namespace, Union[Branch, Tag]]): ...


class GetBranchesResponse(_BauplanIterableCatalogAPIResponse[Branch, None]):
    """
    An Iterable containing bauplan.schema.Branch objects returned by `get_branches` method.

    ## Example:

    ```python notest
    response = client.get_branches()
    for branch in response:
        print(branch.name)
    ```
    """

    ...


class GetTagsResponse(_BauplanIterableCatalogAPIResponse[Tag, None]): ...


class ListJobsResponse(_BauplanIterableRPCResponse['Job', None, get_jobs_pb.GetJobsResponse]):
    """
    An Iterable containing `bauplan.schema.Job` objects returned by `list_jobs` method.

    ## Example:

    ```python notest
    response = client.list_jobs()
    for job in response:
        print(job.id, job.status)
    ```
    """

    ...


class JobState(Enum):
    UNSPECIFIED = common_pb.JobStateType.JOB_STATE_TYPE_UNSPECIFIED
    NOT_STARTED = common_pb.JobStateType.JOB_STATE_TYPE_NOT_STARTED
    RUNNING = common_pb.JobStateType.JOB_STATE_TYPE_RUNNING
    COMPLETE = common_pb.JobStateType.JOB_STATE_TYPE_COMPLETE
    ABORT = common_pb.JobStateType.JOB_STATE_TYPE_ABORT
    FAIL = common_pb.JobStateType.JOB_STATE_TYPE_FAIL
    OTHER = common_pb.JobStateType.JOB_STATE_TYPE_OTHER

    def __str__(self) -> str:
        return {
            JobState.UNSPECIFIED: 'Unspecified',
            JobState.NOT_STARTED: 'Not Started',
            JobState.RUNNING: 'Running',
            JobState.COMPLETE: 'Complete',
            JobState.ABORT: 'Abort',
            JobState.FAIL: 'Fail',
            JobState.OTHER: 'Other',
        }[self]

    @classmethod
    def from_string(cls, state_str: str) -> 'JobState':
        for state in cls:
            if str(state) == state_str:
                return state
        raise ValueError(f"No JobState with string representation '{state_str}'")


class JobKind(Enum):
    """
    Models a job's "kind" or job type. May be one of:
        UNSPECIFIED, CODE_SNAPSHOT_RUN, QUERY, IMPORT_PLAN_CREATE, IMPORT_PLAN_APPLY,
        TABLE_PLAN_CREATE, TABLE_PLAN_CREATE_APPLY, or TABLE_IMPORT.
    """

    UNSPECIFIED = common_pb.JobKind.JOB_KIND_UNSPECIFIED
    CODE_SNAPSHOT_RUN = common_pb.JobKind.JOB_KIND_CODE_SNAPSHOT_RUN
    RUN = common_pb.JobKind.JOB_KIND_CODE_SNAPSHOT_RUN
    QUERY = common_pb.JobKind.JOB_KIND_QUERY_RUN
    IMPORT_PLAN_CREATE = common_pb.JobKind.JOB_KIND_IMPORT_PLAN_CREATE
    IMPORT_PLAN_APPLY = common_pb.JobKind.JOB_KIND_IMPORT_PLAN_APPLY
    TABLE_PLAN_CREATE = common_pb.JobKind.JOB_KIND_TABLE_PLAN_CREATE
    TABLE_PLAN_CREATE_APPLY = common_pb.JobKind.JOB_KIND_TABLE_PLAN_CREATE_APPLY
    TABLE_IMPORT = common_pb.JobKind.JOB_KIND_TABLE_DATA_IMPORT

    def __str__(self) -> str:
        return {
            JobKind.UNSPECIFIED: 'Unknown',
            JobKind.RUN: 'Run',
            JobKind.CODE_SNAPSHOT_RUN: 'CodeSnapshotRun',
            JobKind.QUERY: 'Query',
            JobKind.IMPORT_PLAN_CREATE: 'ImportPlanCreate',
            JobKind.IMPORT_PLAN_APPLY: 'ImportPlanApply',
            JobKind.TABLE_PLAN_CREATE: 'TablePlanCreate',
            JobKind.TABLE_PLAN_CREATE_APPLY: 'TablePlanCreateApply',
            JobKind.TABLE_IMPORT: 'TableImport',
        }[self]

    @classmethod
    def from_string(cls, state_str: str) -> 'JobKind':
        for state in cls:
            if str(state) == state_str:
                return state
        raise ValueError(f"No JobKind with string representation '{state_str}'")


class Job(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    Job is a model for a job in the Bauplan system. It is tracked as a result
    of a code snapshot run.

    """

    id: str
    kind: Union[str, JobKind]
    user: str
    human_readable_status: str
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    status: JobState

    @classmethod
    def from_proto(cls, job_pb: common_pb.JobInfo) -> 'Job':
        return cls(
            id=job_pb.id,
            kind=job_pb.kind,
            user=job_pb.user,
            human_readable_status=job_pb.human_readable_status,
            created_at=proto_datetime_to_py_datetime(job_pb.created_at),
            started_at=proto_datetime_to_py_datetime(job_pb.started_at),
            finished_at=proto_datetime_to_py_datetime(job_pb.finished_at),
            status=JobState(job_pb.status),
        )

    def __str__(self) -> str:
        """Return a string representation of the job."""

        time_annotation = ': '

        # If the job has finished, we can stringify that information
        run_time = self.duration
        if self.finished_at is not None and run_time is not None:
            simplified_finish_dt = self.finished_at.strftime('%m-%d %H:%M')
            simplified_duration = str(timedelta(days=run_time.days, seconds=run_time.seconds))
            time_annotation = f'[{simplified_finish_dt} ({simplified_duration})]: '

        return f'{self.kind} ({self.user}: {self.id_prefix}) {time_annotation}{self.human_readable_status}'

    @property
    def id_prefix(self) -> str:
        """Return the first 8 characters of the job ID."""
        return self.id[:8] if self.id else ''

    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate the duration between created_at and finished_at."""
        if self.created_at is not None and self.finished_at is not None:
            return self.finished_at - self.created_at
        if self.created_at is not None:
            return datetime.now() - self.created_at
        return None

    @property
    def is_running(self) -> bool:
        """Check if the job is currently running."""
        return self.status == JobState.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if the job has completed (successfully)."""
        return self.status == JobState.COMPLETE

    @property
    def is_failed(self) -> bool:
        """Check if the job has failed."""
        return self.status == JobState.FAIL

    @property
    def is_aborted(self) -> bool:
        """Check if the job has been aborted."""
        return self.status == JobState.ABORT

    def has_id(self, check_id: str) -> bool:
        """Check if the job has the specified ID or ID prefix."""
        if len(check_id) == len(self.id) or len(check_id) == 8:
            return self.id.startswith(check_id)
        return False

    def has_status(self, check_status: Union[str, JobState] = JobState.COMPLETE) -> bool:
        """Check if the job has specified status."""
        if isinstance(check_status, str):
            return str(self.status) == check_status
        return self.status == check_status

    def finished_before(self, end: datetime) -> bool:
        """Check if the job finished before the given timedelta from now."""
        return self.finished_at is not None and self.finished_at <= end

    def finished_after(self, start: datetime) -> bool:
        """Check if the job finished within the given timedelta from now."""
        return self.finished_at is not None and self.finished_at >= start

    def finished_between(self, start: datetime, end: datetime) -> bool:
        """Check if the job finished between two datetimes."""
        return self.finished_after(start) and self.finished_before(end)

    def has_finished_range(
        self,
        *,  # From here only keyword arguments are allowed
        after_time: Optional[datetime] = None,
        before_time: Optional[datetime] = None,
    ) -> bool:
        if after_time is not None and before_time is not None:
            return self.finished_between(after_time, before_time)

        if after_time is not None:
            return self.finished_after(after_time)

        if before_time is not None:
            return self.finished_before(before_time)

        # Should be same as if filter was not provided
        return True

    def started_before(self, end: datetime) -> bool:
        """Check if the job started before the given datetime."""
        return self.created_at is not None and self.created_at <= end

    def started_after(self, start: datetime) -> bool:
        """Check if the job started after the given datetime."""
        return self.created_at is not None and self.created_at >= start

    def started_between(self, start: datetime, end: datetime) -> bool:
        """Check if the job started between two datetimes."""
        return self.started_after(start) and self.started_before(end)

    def has_started_range(
        self,
        *,  # From here only keyword arguments are allowed
        after_time: Optional[datetime] = None,
        before_time: Optional[datetime] = None,
    ) -> bool:
        """Check if the job started within the specified time range."""
        if after_time is not None and before_time is not None:
            return self.started_between(after_time, before_time)

        if after_time is not None:
            return self.started_after(after_time)

        if before_time is not None:
            return self.started_before(before_time)

        # Should be same as if filter was not provided
        return True


class JobLogStream(Enum):
    STDOUT = runner_events_pb.RuntimeLogEvent.OutputStream.OUTPUT_STREAM_STDOUT
    STDERR = runner_events_pb.RuntimeLogEvent.OutputStream.OUTPUT_STREAM_STDERR

    @classmethod
    def _from_pb(cls, log_pb: runner_events_pb.RuntimeLogEvent) -> Optional[JobLogStream]:
        match log_pb.output_stream:
            case runner_events_pb.RuntimeLogEvent.OUTPUT_STREAM_STDOUT:
                return JobLogStream.STDOUT

            case runner_events_pb.RuntimeLogEvent.OUTPUT_STREAM_STDERR:
                return JobLogStream.STDERR

            case _:
                return None


class JobLogLevel(Enum):
    ERROR = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_ERROR
    WARN = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_WARNING
    DEBUG = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_DEBUG
    INFO = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_INFO
    TRACE = runner_events_pb.RuntimeLogEvent.LOG_LEVEL_TRACE

    @classmethod
    def _from_pb(cls, log_pb: runner_events_pb.RuntimeLogEvent) -> Optional[JobLogLevel]:
        match log_pb.level:
            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_ERROR:
                return JobLogLevel.ERROR

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_WARNING:
                return JobLogLevel.WARN

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_DEBUG:
                return JobLogLevel.DEBUG

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_INFO:
                return JobLogLevel.INFO

            case runner_events_pb.RuntimeLogEvent.LOG_LEVEL_TRACE:
                return JobLogLevel.TRACE

            case _:
                return None


class JobLogEvent(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobLogEvent is a model for a particular log message from a particular job.

    When you output logs within a Python model, they are persisted as JobLogEvents.

    """

    stream: Optional[JobLogStream]
    level: Optional[JobLogLevel]
    message: str

    @classmethod
    def _from_pb(
        cls,
        event_pb: runner_events_pb.RunnerEvent,
        filter_by_type: Optional[runner_events_pb.RuntimeLogEvent.LogType],
    ) -> Optional[JobLogEvent]:
        if event_pb.HasField('runtime_user_log'):
            log_pb = event_pb.runtime_user_log

            if filter_by_type is None or log_pb.type == filter_by_type:
                return cls(
                    stream=JobLogStream._from_pb(log_pb),
                    level=JobLogLevel._from_pb(log_pb),
                    message=log_pb.msg,
                )

        return None

    @property
    def stream_name(self) -> str:
        return self.stream.name if self.stream is not None else ''

    @property
    def level_name(self) -> str:
        return self.level.name if self.level is not None else ''


# TODO: I think this should be the JobLog, because it's the actual log.
#       When we remove the JobLog alias (breaking change) maybe we can rename this
class JobLogList(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobLogList is a model for all of the logs from a particular job. This model is primarily
    provided as a convenience for "common" interactions with a job's log messages.

    """

    events: List[JobLogEvent]

    @classmethod
    def _from_pb(
        cls,
        getlog_pb: get_logs_pb.GetLogsResponse,
        filter_by_type: runner_events_pb.RuntimeLogEvent.LogType = runner_events_pb.RuntimeLogEvent.LOG_TYPE_USER,
    ) -> JobLogList:
        log_events = []

        for runner_event in getlog_pb.events:
            job_log_event = JobLogEvent._from_pb(runner_event, filter_by_type=filter_by_type)

            if job_log_event is not None:
                log_events.append(job_log_event)

        return cls(events=log_events)

    @property
    def log_events(self) -> List[JobLogEvent]:
        return self.events

    def error_messages(self) -> list[str]:
        error_log_events = list(filter(lambda log: log.level == JobLogLevel.ERROR, self.events))
        if len(error_log_events) == 0:
            error_log_events = ['No error messages']

        return list(map(str, error_log_events))


class CacheDir(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    CacheDir is a model for a standard bauplan directory ($HOME/.bauplan) for caching of files on
    the local filesystem. This is partially a convenience interface for other models such as
    JobContext, and partially a convenience for the user to easily clean up any cache files they no
    longer want (or a previous process failed to clean up).

    """

    _fs_tmpdir: Optional[TemporaryDirectory] = PrivateAttr(default=None)
    _is_persistent: bool = PrivateAttr(default=False)
    dirpath: Path

    @classmethod
    def _for_job(
        cls,
        job_id: str,
        base_dirpath: Path = HOME_DIRPATH / '.bauplan',
        dirname_prefix: str = '._job_snapshot_',
    ) -> Optional[CacheDir]:
        tmpdir = TemporaryDirectory(
            prefix=f'{dirname_prefix}{job_id}',
            dir=base_dirpath,
            delete=False,
        )

        if tmpdir is None:
            return None

        cache_dir = CacheDir(dirpath=Path(tmpdir.name))
        cache_dir._fs_tmpdir = tmpdir
        cache_dir._is_persistent = False
        return cache_dir

    @classmethod
    def clear_job_cache(cls, base_dirpath: Path = HOME_DIRPATH / '.bauplan') -> None:
        """Remove all directories with the '._job_snapshot_' prefix from the bauplan cache."""
        for walk_path, dirnames, _ in base_dirpath.walk():
            for dirname in dirnames:
                if dirname.startswith('._job_snapshot_'):
                    shutil.rmtree(walk_path / dirname)

    def __del__(self) -> None:
        # If called implicitly, check `_is_persistent` flag
        if self._fs_tmpdir is not None and not self._is_persistent:
            self._fs_tmpdir.cleanup()

    def cleanup(self) -> None:
        """
        Remove the temporary cache directory and its contents.
        """
        self._is_persistent = False

        # If called explicitly, ignore `_is_persistent` flag
        if self._fs_tmpdir is not None:
            self._fs_tmpdir.cleanup()

    def save(self) -> None:
        """
        Make the temporary cache directory persistent, preventing automatic cleanup.
        """
        self._is_persistent = True


class JobContext(BaseModel):
    """
    EXPERIMENTAL AND SUBJECT TO CHANGE.

    JobContext is a model for immediate working context of a particular job. This currently
    includes: (1) Ref, (2) Code Snapshot, (3) Logs. A JobContext should enable a variety of
    workflows for iterating on an existing Job.

    """

    id: str
    project_id: Optional[str]
    project_name: Optional[str]

    ref: Optional[Ref]
    tx_ref: Optional[Ref]

    logs: List[JobLogEvent]
    dag_nodes: List[DAGNode]
    dag_edges: List[DAGEdge]

    dag_nodes: List[DAGNode]
    dag_edges: List[DAGEdge]

    snapshot_dict: Dict[str, str]
    snapshot_dirpath: Optional[Path]
    _snapshot_tmpdir: Optional[CacheDir] = PrivateAttr(default=None)

    @classmethod
    def _from_pb(cls, get_context_pb: job_context_pb.GetJobContextResponse) -> List[JobContext]:
        """Extract data from the response of a GetJobContext request."""

        job_contexts = []

        # A response returns many JobContext messages (one for each requested job).
        for job_ctx_pb in get_context_pb.job_contexts:
            # Construct a JobContext instance for each JobContext message.
            job_ctx = cls._from_pb_jobctx(job_ctx_pb)

            if job_ctx is not None:
                job_contexts.append(job_ctx)

        return job_contexts

    @classmethod
    def _decompress_snapshot_fsdir(cls, snapshot_zip: bytes, snapshot_dirpath: Path) -> bool:
        """
        Handles decompression of a code snapshot zipfile.

        :job_id: A string that identifies the location of the decompressed zip file.

        """

        try:
            with zipfile.ZipFile(file=io.BytesIO(snapshot_zip)) as zip_handle:
                for archive_member in zip_handle.namelist():
                    zip_handle.extract(archive_member, path=snapshot_dirpath)

        except Exception as decompress_err:
            warnings.warn(
                f'Failed to decompress code snapshot {decompress_err}',
                stacklevel=1,
            )
            return False

        return True

    @classmethod
    def _decompress_snapshot_inmem(cls, snapshot_zip: bytes) -> dict[str, str]:
        """
        Handles decompression of a code snapshot zipfile to a dictionary.

        """

        snapshot_data = {}

        try:
            with zipfile.ZipFile(file=io.BytesIO(snapshot_zip)) as zip_handle:
                for archive_member in zip_handle.namelist():
                    with zip_handle.open(archive_member) as member_handle:
                        snapshot_data[archive_member] = member_handle.read()

        except Exception as decompress_err:
            warnings.warn(
                f'Failed to decompress code snapshot {decompress_err}',
                stacklevel=1,
            )
            return {}

        return snapshot_data

    @classmethod
    def _from_pb_jobctx(cls, job_ctx_pb: job_context_pb.JobContext, use_cache_dir: bool = True) -> JobContext:
        # Grab easy fields first
        id_prefix = job_ctx_pb.job_id[:8]
        job_ref = Ref(name=job_ctx_pb.ref)

        job_txref = None
        if job_ctx_pb.transaction_branch is not None:
            job_txref = Ref(name=job_ctx_pb.transaction_branch.name)

        # Collect user events from the returned events
        job_logs = []
        for runner_event in job_ctx_pb.job_events:
            log_event = JobLogEvent._from_pb(
                runner_event, filter_by_type=runner_events_pb.RuntimeLogEvent.LOG_TYPE_USER
            )

            if log_event is not None:
                job_logs.append(log_event)

        # Decompress the snapshots into a local directory (cache dir) or into memory (dict)
        job_snap_datadict = {}
        job_snap_cachedir = None
        job_snap_cachedirpath = None

        # Check it is not None, not empty string, and not empty binary string
        if job_ctx_pb.code_snapshot:
            if not use_cache_dir:
                job_snap_datadict = cls._decompress_snapshot_inmem(job_ctx_pb.code_snapshot)

            else:
                job_snap_cachedir = CacheDir._for_job(id_prefix)
                if job_snap_cachedir is not None:
                    job_snap_cachedirpath = job_snap_cachedir.dirpath
                    cls._decompress_snapshot_fsdir(job_ctx_pb.code_snapshot, job_snap_cachedirpath)

        # Extract DAG representation
        job_dag_nodes = []
        if job_ctx_pb.models is not None:
            job_dag_nodes = [
                DAGNode(id=model_node.model_id, name=model_node.model_name)
                for model_node in job_ctx_pb.models
            ]

        job_dag_edges = []
        if job_ctx_pb.model_deps is not None:
            job_dag_edges = [
                DAGEdge(source_model=model_edge.source_id, destination_model=model_edge.destination_id)
                for model_edge in job_ctx_pb.model_deps
            ]

        # Construct a JobContext instance to return, but defer snapshot handling
        job_context = JobContext(
            id=job_ctx_pb.job_id,
            project_id=job_ctx_pb.project_id,
            project_name=job_ctx_pb.project_name,
            ref=job_ref,
            tx_ref=job_txref,
            logs=job_logs,
            dag_nodes=job_dag_nodes,
            dag_edges=job_dag_edges,
            snapshot_dict=job_snap_datadict,
            snapshot_dirpath=job_snap_cachedirpath,
        )
        job_context._snapshot_tmpdir = job_snap_cachedir
        return job_context

    def __str__(self) -> str:
        cache_location = 'No snapshots cached'
        if self._snapshot_tmpdir is not None:
            cache_location = f'[Temporary] Cache Dir: {self.snapshot_dirpath}'

            if self._snapshot_tmpdir._is_persistent:
                cache_location = f'[Persistent] Cache Location: {self.snapshot_dirpath}'

        return f'{self.id}\n\tRef: {self.ref}\n\tTransactional Ref: {self.tx_ref}\n\t{cache_location}'

    def cleanup_cache(self) -> None:
        """
        Clean up the cache directory if it exists.
        """
        if self._snapshot_tmpdir is not None:
            self._snapshot_tmpdir.cleanup()

    def save_cache(self) -> None:
        """
        Save the cache directory if it exists.
        """
        if self._snapshot_tmpdir is not None:
            self._snapshot_tmpdir.save()
