from typing import Dict, Iterable, List, Optional, Union

from google.protobuf.json_format import MessageToJson

from bauplan._bpln_proto.commander.service.v2.subscribe_logs_pb2 import (
    SubscribeLogsRequest,
    SubscribeLogsResponse,
)

from ._bpln_proto.commander.service.v2.common_pb2 import JobRequestCommon
from ._bpln_proto.commander.service.v2.external_table_create_pb2 import (
    ExternalTableCreateRequest,
    ExternalTableCreateResponse,
    SearchUris,
)
from ._common import BAUPLAN_VERSION, CLIENT_HOSTNAME
from ._common_operation import (
    _JobLifeCycleHandler,
    _lifecycle,
    _OperationContainer,
    _print_planner_logs,
)
from ._run import JobStatus
from ._validators import _Validate
from .state import ExternalTableCreateContext, ExternalTableCreateState


def _handle_log(
    log: SubscribeLogsResponse,
    run_state: ExternalTableCreateState,
    debug: Optional[bool],
    verbose: Optional[bool],
) -> bool:
    runner_event = log.runner_event
    event_type = runner_event.WhichOneof('event')
    if event_type == 'job_completion':
        match runner_event.job_completion.WhichOneof('outcome'):
            case 'success':
                run_state.job_status = JobStatus.success
            case 'failure':
                run_state.job_status = JobStatus.failed
                run_state.error = runner_event.job_completion.failure.error_message
            case 'rejected':
                run_state.job_status = JobStatus.rejected
            case 'cancellation':
                run_state.job_status = JobStatus.cancelled
            case 'timeout':
                run_state.job_status = JobStatus.timeout
            case 'heartbeat_failure':
                run_state.job_status = JobStatus.heartbeat_failure
            case _:
                run_state.job_status = JobStatus.unknown
        return True
    return False


class _ExternalTableCreate(_OperationContainer):
    @_lifecycle
    def create_external_table_from_parquet(
        self,
        table_name: str,
        search_patterns: List[str],
        branch_name: Optional[str] = None,
        namespace: Optional[str] = None,
        overwrite: bool = False,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        # internal
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
        detach: bool = False,
    ) -> ExternalTableCreateState:
        """
        Create an external table from files.
        This is the equivalent of running through the CLI the `bauplan table create external` command.

        This uses a _JobLifecyleHandler to handle timeout issues (future: KeyboardInterrupt)
        We register the job_id, log_stream, and flight_client with the lifecycle_handler
        so we can do a graceful shutdown behind the scenes upon TimeoutError exception.
        """

        if lifecycle_handler is None:
            raise Exception('internal error: lifecycle_handler is required')

        # Params validation
        search_patterns = _Validate.string_list('search_patterns', search_patterns)
        table_name = _Validate.string('table_name', table_name)
        branch_name = _Validate.optional_ref('ref', branch_name, self.profile.branch)
        namespace = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        overwrite = _Validate.boolean('overwrite', overwrite)
        debug, debug_flag = _Validate.pb2_optional_boolean('debug', debug, self.profile.debug)
        args = _Validate.args('args', args, self.profile.args)
        verbose = _Validate.optional_boolean('verbose', verbose, self.profile.verbose)
        detach = _Validate.boolean('detach', detach)
        priority = _Validate.optional_int('priority', priority)

        # We can now submit the request
        client_v2, metadata = self._common.get_commander_v2_and_metadata(args)

        job_request_common = JobRequestCommon(
            module_version=BAUPLAN_VERSION,
            hostname=CLIENT_HOSTNAME,
            args=args,
            debug=debug_flag,
        )
        if priority is not None:
            job_request_common.priority = priority

        create_request = ExternalTableCreateRequest(
            job_request_common=job_request_common,
            branch_name=branch_name,
            table_name=table_name,
            namespace=namespace,
            overwrite=overwrite,
        )

        # Set the input source
        create_request.input_files.CopyFrom(SearchUris(uris=search_patterns))

        if debug or verbose:
            print(
                'ExternalTableCreateRequest',
                'request',
                MessageToJson(create_request),
            )

        create_response: ExternalTableCreateResponse = client_v2.ExternalTableCreate(
            create_request, metadata=metadata
        )
        if debug or verbose:
            print(
                'ExternalTableCreateResponse',
                'job_id',
                create_response.job_response_common.job_id,
                'response',
                MessageToJson(create_response),
            )
        _print_planner_logs(create_response.job_response_common.logs, debug or verbose)

        state = ExternalTableCreateState(
            job_id=create_response.job_response_common.job_id,
            ctx=ExternalTableCreateContext(
                branch_name=create_response.branch_name,
                table_name=create_response.table_name,
                namespace=create_response.namespace,
                input_files=search_patterns,
                overwrite=overwrite,
                debug=create_response.job_response_common.debug,
                detach=detach,
            ),
        )

        if detach:
            return state

        job_id = create_response.job_response_common.job_id
        lifecycle_handler.register_job_id(job_id)

        # Subscribe to logs
        log_stream: Iterable[SubscribeLogsResponse] = client_v2.SubscribeLogs(
            SubscribeLogsRequest(job_id=job_id),
            metadata=metadata,
        )
        lifecycle_handler.register_log_stream(log_stream)
        # ATM there is no termination event so runner only sends a "JobComplete"
        for log in log_stream:
            if verbose:
                print('log_stream:', log)
            _handle_log(log, state, debug, verbose)
        return state
