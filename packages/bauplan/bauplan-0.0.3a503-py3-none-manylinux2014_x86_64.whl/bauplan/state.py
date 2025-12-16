import datetime
import time
from typing import Dict, List, Optional

from bauplan._bpln_proto.commander.service.v2.runner_events_pb2 import RunnerEvent, RuntimeLogEvent

# from ._protobufs.commander_pb2 import (
#     RunnerEvent,
#     RuntimeLogEvent,
# )
from .schema import _BauplanData


class CommonRunState:
    """
    CommonRunState tracks information about what happened during the course of a Bauplan
    job run.

    Attributes:
        user_logs (List[str]): A list of user log messages.
        runner_events (List[RunnerEvent]): A list of runner events.
        runtime_logs (List[RuntimeLogEvent]): A list of runtime log events.
        tasks_started (Dict[str, datetime.datetime]): A dictionary mapping task IDs to their start times.
        tasks_stopped (Dict[str, datetime.datetime]): A dictionary mapping task IDs to their stop times.
        job_status (Optional[str]): The status of the job (e.g., "success", "failure").
        started_at_ns (int): The start time of the job in nanoseconds since the epoch.
        ended_at_ns (Optional[int]): The end time of the job in nanoseconds since the epoch.
    """

    user_logs: List[str]
    runner_events: List[RunnerEvent]
    runtime_logs: List[RuntimeLogEvent]
    tasks_started: Dict[str, datetime.datetime]
    tasks_stopped: Dict[str, datetime.datetime]
    job_status: Optional[str]
    started_at_ns: int
    ended_at_ns: Optional[int]

    @property
    def duration(self) -> Optional[float]:
        if self.ended_at_ns is not None:
            return (self.ended_at_ns - self.started_at_ns) / 1_000_000_000
        return None

    @property
    def duration_ns(self) -> Optional[int]:
        if self.ended_at_ns is not None:
            return self.ended_at_ns - self.started_at_ns
        return None


class RunExecutionContext(_BauplanData):
    snapshot_id: str
    snapshot_uri: str
    project_dir: str
    ref: str
    namespace: str
    dry_run: bool
    transaction: str
    strict: str
    cache: str
    preview: str
    debug: bool
    detach: bool


class RunState(CommonRunState):
    """
    RunState tracks information about what happened during the course of a Bauplan
    job run (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions, project directory,
    job status, and failed fatal task description.

    Attributes:
        job_id (str): The ID of the job.
        ctx (`bauplan.state.RunExecutionContext`): The execution context of the run.

    """

    job_id: Optional[str]
    ctx: RunExecutionContext

    def __init__(
        self,
        job_id: str,
        ctx: RunExecutionContext,
        started_at_ns: Optional[int] = None,
    ) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.started_at_ns = started_at_ns or time.time_ns()
        self.user_logs = []
        self.runner_events = []
        self.runtime_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.job_status = None


class ReRunExecutionContext(_BauplanData):
    """
    ReRunExecutionContext tracks information about the context in which a Bauplan job rerun is
    executed.

    Attributes:
        re_run_job_id (str): The ID of the rerun job.
        ref (str): The ref, branch name or tag name which to used for rerun.
        namespace (str): The namespace in which the rerun is executed.
        dry_run (bool): Whether the rerun is a dry run.
        transaction (str): Whether to enable or disable transaction mode for the run (e.g., "on" or "off").
        strict (str): Whether to enable or disable strict schema validation (e.g., "on" or "off").
        cache (str): Whether to enable or disable caching for the run. (e.g., "on" or "off").
        preview (str): Whether there is a preview mode for the rerun ('on'/'off'/'head'/'tail').
        debug (bool): Whether debug mode is enabled for the rerun.

    """

    re_run_job_id: str
    ref: str
    namespace: str
    dry_run: bool
    transaction: str
    strict: str
    cache: str
    preview: str
    debug: bool


class ReRunState(CommonRunState):
    """
    ReRunState tracks information about what happened during the course of a Bauplan
    job rerun (executed DAG).

    It represents the state of a run, including job ID, task lifecycle events, user logs,
    task start and stop times, failed nonfatal task descriptions,
    job status, and failed fatal task description.

    Attributes:
        job_id (str): The ID of the job.
        run_id (str): The ID of the run.
        ctx (`bauplan.state.ReRunExecutionContext`): The execution context of the rerun.

    """

    job_id: str
    run_id: str
    ctx: ReRunExecutionContext

    def __init__(
        self,
        job_id: str,
        ctx: ReRunExecutionContext,
        started_at_ns: Optional[int] = None,
    ) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.started_at_ns = started_at_ns or time.time_ns()
        self.user_logs = []
        self.runner_events = []
        self.runtime_logs = []
        self.tasks_started = {}
        self.tasks_stopped = {}
        self.job_status = None


class PlanImportState:
    """
    PlanImportState tracks information about what happened during the course of an "plan import" job
    that plans a job to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    plan: Optional[Dict] = None
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []


class ApplyPlanState:
    """
    ApplyPlanState tracks information about what happened during the course of an "apply import plan" job
    that executes the plan to import a table from cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    """

    job_id: str
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.runner_events = []


class TableCreatePlanContext(_BauplanData):
    branch_name: str
    table_name: str
    table_replace: bool
    table_partitioned_by: Optional[str]
    namespace: str
    search_string: str
    debug: bool


class TableCreatePlanState:
    """
    TableCreatePlanState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    ctx: TableCreatePlanContext
    plan: Optional[Dict]
    error: Optional[str] = None
    can_auto_apply: Optional[bool] = None
    files_to_be_imported: List[str]
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableCreatePlanContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []
        self.files_to_be_imported = []


class TableCreatePlanApplyContext(_BauplanData):
    debug: bool


class TableCreatePlanApplyState:
    """
    TableCreatePlanApplyState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    """

    job_id: str
    ctx: TableCreatePlanApplyContext
    plan: Optional[str] = None
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableCreatePlanApplyContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []


class TableDataImportContext(_BauplanData):
    branch_name: str
    table_name: str
    namespace: str
    search_string: str
    import_duplicate_files: bool
    best_effort: bool
    continue_on_error: bool
    transformation_query: Optional[str]
    preview: str
    debug: bool
    detach: bool


class TableDataImportState:
    """
    TableDataImportState tracks information about what happened during the course of an "table create" job
    that plans a job to create an empty table based on your cloud storage to your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    It also includes the output of the job: a string containing the YAML of the import plan.

    Attributes:
        job_id (str): The ID of the job.
        ctx (`bauplan.state.TableDataImportContext`): The execution context of the table data import.
        error (Optional[str]): An optional error message if the job failed.
        job_status (Optional[str]): The status of the job (e.g., "SUCCESS", "FAILED").
        runner_events (Optional[List[RunnerEvent]]): A list of runner events associated with the job.
    """

    job_id: str
    ctx: TableDataImportContext
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: TableDataImportContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []
        self.files_to_be_imported = []


class ExternalTableCreateContext(_BauplanData):
    branch_name: str
    table_name: str
    namespace: str
    input_files: Optional[List[str]]
    overwrite: bool
    debug: bool
    detach: bool


class ExternalTableCreateState:
    """
    ExternalTableCreateState tracks information about what happened during the course of an "external table create" job
    that creates an external table based on S3 files or Iceberg metadata in your Bauplan data catalog.

    It represents the state of the job, including job ID, job status (failure/success),
    error description (if any), and a list of events describing each step of the job.

    """

    job_id: str
    ctx: ExternalTableCreateContext
    error: Optional[str] = None
    job_status: Optional[str] = None
    runner_events: Optional[List[RunnerEvent]]

    def __init__(self, job_id: str, ctx: ExternalTableCreateContext) -> None:
        self.job_id = job_id
        self.ctx = ctx
        self.runner_events = []
