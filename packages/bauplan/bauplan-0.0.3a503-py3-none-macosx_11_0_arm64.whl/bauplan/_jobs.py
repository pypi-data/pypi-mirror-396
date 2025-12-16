import time
from typing import List, Optional, Union

from google.protobuf.timestamp_pb2 import Timestamp

from ._bpln_proto.commander.service.v2 import (
    CancelJobRequest,
    GetJobContextRequest,
    GetJobsRequest,
    GetLogsRequest,
    JobId,
)
from ._bpln_proto.commander.service.v2.get_jobs_pb2 import GetJobsResponse
from ._common_operation import _OperationContainer
from .errors import (
    JobAmbiguousPrefixError,
    JobCancelError,
    JobContextError,
    JobGetError,
    JobLogsError,
    JobNotFoundError,
    JobsListError,
)
from .schema import (
    Job,
    JobContext,
    JobLogList,
    JobState,
    ListJobsResponse,
)


class _Jobs(_OperationContainer):
    """Implements operations for retrieving jobs and logs."""

    def get_job(self, job_id: str) -> Job:
        """
        Retrieve job matching the specified ID or ID prefix.
        """

        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        req = GetJobsRequest(
            job_ids=[job_id],
            all_users=True,
            max_records=1,
        )

        try:
            resp = client_v2.GetJobs(req, metadata=metadata)
        except Exception as e:
            raise JobGetError(job_id) from e

        if len(resp.jobs) != 1:
            raise JobNotFoundError(job_id)
        if resp.pagination_token:
            raise JobAmbiguousPrefixError(job_id)

        return Job.from_proto(resp.jobs[0])

    def get_jobs(
        self,
        all_users: Optional[bool] = None,
        *,  # From here only keyword arguments are allowed
        filter_by_ids: Optional[List[str]] = None,
        filter_by_kinds: Optional[List[int]] = None,
        filter_by_users: Optional[List[str]] = None,
        filter_by_statuses: Optional[List[int]] = None,
        filter_by_created_before: Optional[Timestamp] = None,
        filter_by_created_after: Optional[Timestamp] = None,
        limit: Optional[int] = None,
        itersize: int = 100,
    ) -> ListJobsResponse:
        """
        List (retrieve) all jobs for the user or (optionally) for the organization.

        The filtering parameters apply server-side filtering.

        Filters:
        filter_by_ids: Filters received jobs by their IDs or ID prefixes.
        filter_by_kinds: Filters received jobs by their JobKind.
        filter_by_users: Filters received jobs by user.
        filter_by_statuses: Filters received jobs by their JobState status.
        filter_by_created_before: Filters jobs created before this timestamp.
        filter_by_created_after: Filters jobs created after this timestamp.
        limit: Maximum number of jobs to return (across all pages).
        itersize: Number of jobs to fetch per page.
        """

        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        def _fetcher(max_records: int, pagination_token: Optional[str]) -> GetJobsResponse:
            req = GetJobsRequest(
                job_ids=filter_by_ids,
                all_users=all_users or False,
                filter_users=filter_by_users,
                filter_kinds=filter_by_kinds,
                filter_statuses=filter_by_statuses,
                filter_created_after=filter_by_created_after,
                filter_created_before=filter_by_created_before,
                max_records=max_records,
                pagination_token=pagination_token or '',
            )

            try:
                return client_v2.GetJobs(req, metadata=metadata)
            except Exception as e:
                raise JobsListError(f'Failed to list jobs: {e}') from e

        return ListJobsResponse(
            data_fetcher=_fetcher,
            data_mapper=Job.from_proto,
            items_extractor=lambda resp: resp.jobs,
            token_extractor=lambda resp: resp.pagination_token or None,
            itersize=itersize,
            limit=limit,
        )

    def get_logs(self, job: Union[str, Job]) -> JobLogList:
        """
        Retrieve *only user logs* for one job by matching a prefix of its ID.

        Steps:
        1) Call GetLogs on each provided job ID.
        2) Gather user logs from RunnerEvents in response.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        # Use the provided ID or extract from provided job
        query_jobid = job if isinstance(job, str) else job.id_prefix

        logs_req = GetLogsRequest(job_id=query_jobid)
        try:
            logs_resp = client_v2.GetLogs(logs_req, metadata=metadata)
        except Exception as e:
            raise JobLogsError(query_jobid) from e

        # TODO: optionally add server-side filters
        return JobLogList._from_pb(logs_resp)

    def get_contexts(
        self,
        jobs: Union[List[str], List[Job]],
        include_logs: bool = False,
        include_snapshot: bool = False,
    ) -> List[JobContext]:
        """
        Retrieve a JobContext for each entry in jobs, which is a list of job IDs or a list of Job
        instances.

        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)

        # Use the provided ID or extract from provided job
        query_jobids = [job if isinstance(job, str) else job.id for job in jobs]

        jobctx_req = GetJobContextRequest(
            job_ids=query_jobids,
            include_logs=include_logs,
            include_snapshot=include_snapshot,
        )
        try:
            jobctx_resp = client_v2.GetJobContext(jobctx_req, metadata=metadata)
        except Exception:
            raise JobContextError(query_jobids) from None

        return JobContext._from_pb(jobctx_resp)

    def cancel_job(self, id: str) -> None:
        """
        Cancels a running job and polls its status to verify it has been
        cancelled.
        """
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args=None)
        req = CancelJobRequest(job_id=JobId(id=id))

        try:
            client_v2.CancelJob(req, metadata=metadata)
        except Exception as e:
            raise JobCancelError(id, f'Failed to cancel job {id}: {e}') from e

        retry_count = 0
        encountered_states = []

        while retry_count < 10:
            job = self.get_job(id)
            encountered_states.append(job.status)

            if job.status == JobState.ABORT:
                return

            retry_count += 1
            time.sleep(1)

        raise JobCancelError(
            id, f'Could not verify job was cancelled. Encountered states: {encountered_states}'
        )
