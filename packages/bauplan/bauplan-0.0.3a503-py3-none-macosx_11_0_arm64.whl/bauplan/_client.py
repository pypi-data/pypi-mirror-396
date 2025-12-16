from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Literal, Optional, Tuple, Union, cast

import grpc._channel
import pyarrow as pa
import pydantic
import requests

from bauplan._jobs import _Jobs

from . import exceptions
from ._common import BAUPLAN_VERSION, Constants
from ._common_operation import _JobLifeCycleHandler, _lifecycle, _OperationContainer
from ._external_table_create import ExternalTableCreateState, _ExternalTableCreate
from ._info import InfoState, _Info
from ._profile import Profile
from ._query import _Query
from ._run import ReRunState, RunState, _Run
from ._table_create_plan import TableCreatePlanApplyState, TableCreatePlanState, _TableCreate
from ._table_data_import import TableDataImportState, _TableImport
from ._validators import _Validate
from .errors import BauplanError, JobAmbiguousError, JobContextError, ParameterMissingRequiredValuesError
from .schema import (
    APIResponse,
    APIResponseWithData,
    APIResponseWithError,
    Branch,
    Commit,
    DateRange,
    GetBranchesResponse,
    GetCommitsResponse,
    GetNamespacesResponse,
    GetTablesResponse,
    GetTagsResponse,
    Job,
    JobContext,
    JobKind,
    JobLog,
    JobState,
    ListJobsResponse,
    Namespace,
    Ref,
    Table,
    TableWithMetadata,
    Tag,
)


class Client(_OperationContainer):
    """
    A consistent interface to access Bauplan operations.

    #### Using the client

    ```python
    import bauplan
    client = bauplan.Client()

    # query the table and return result set as an arrow Table
    my_table = client.query('SELECT avg(age) AS average_age FROM bauplan.titanic limit 1', ref='main')

    # efficiently cast the table to a pandas DataFrame
    df = my_table.to_pandas()
    ```

    #### Notes on authentication

    ```python notest
    # by default, authenticate from BAUPLAN_API_KEY >> BAUPLAN_PROFILE >> ~/.bauplan/config.yml
    client = bauplan.Client()
    # client used ~/.bauplan/config.yml profile 'default'

    os.environ['BAUPLAN_PROFILE'] = "someprofile"
    client = bauplan.Client()
    # >> client now uses profile 'someprofile'

    os.environ['BAUPLAN_API_KEY'] = "mykey"
    client = bauplan.Client()
    # >> client now authenticates with api_key value "mykey", because api key > profile

    # specify authentication directly - this supercedes BAUPLAN_API_KEY in the environment
    client = bauplan.Client(api_key='MY_KEY')

    # specify a profile from ~/.bauplan/config.yml - this supercedes BAUPLAN_PROFILE in the environment
    client = bauplan.Client(profile='default')
    ```

    #### Handling Exceptions

    Catalog operations (branch/table methods) raise a subclass of `bauplan.exceptions.BauplanError` that mirror HTTP status codes.
        - 400: `bauplan.exceptions.InvalidDataError`
        - 401: `bauplan.exceptions.UnauthorizedError`
        - 403: `bauplan.exceptions.AccessDeniedError`
        - 404: `bauplan.exceptions.ResourceNotFoundError` e.g .ID doesn't match any records
        - 404: `bauplan.exceptions.ApiRouteError` e.g. the given route doesn't exist
        - 405: `bauplan.exceptions.ApiMethodError` e.g. POST on a route with only GET defined
        - 409: `bauplan.exceptions.UpdateConflictError` e.g. creating a record with a name that already exists
        - 429: `bauplan.exceptions.TooManyRequestsError`

    Run/Query/Scan/Import operations raise a subclass of `bauplan.exceptions.BauplanError` that represents, and also return a `bauplan.state.RunState` object containing details and logs:
        - `bauplan.exceptions.JobError` e.g. something went wrong in a run/query/import/scan; includes error details

    Run/import operations also return a state object that includes a `job_status` and other details.
    There are two ways to check status for run/import operations:
        1. try/except `bauplan.exceptions.JobError`
        2. check the `state.job_status` attribute

    ## Examples

    ```python notest
    state = client.run(...)
    if state.job_status != "SUCCESS":
        ...
    ```

    Parameters:
        profile: The Bauplan config profile name to use to determine api_key.
        api_key: Your unique Bauplan API key; mutually exclusive with `profile`. If not provided, fetch precedence is 1) environment `BAUPLAN_API_KEY` 2) .bauplan/config.yml
        branch: The default branch to use for queries and runs. If not provided `active_branch` from the profile is used.
        namespace: The default namespace to use for queries and runs.
        cache: Whether to enable or disable caching for all the requests.
        debug: Whether to enable or disable debug mode for all the requests.
        verbose: Whether to enable or disable verbose mode for all the requests.
        args: Additional arguments to pass to all the requests.
        api_endpoint: The Bauplan API endpoint to use. If not provided, fetch precedence is 1) environment `BAUPLAN_API_ENDPOINT` 2) .bauplan/config.yml
        catalog_endpoint: The Bauplan catalog endpoint to use. If not provided, fetch precedence is 1) environment `BAUPLAN_CATALOG_ENDPOINT` 2) .bauplan/config.yml
        itersize: The maximum number of records to fetch, per page.
        client_timeout: The client timeout in seconds for all the requests.
        env: The environment to use for all the requests. Default: 'prod'.
        config_file_path: The path to the Bauplan config file to use. If not provided, fetch precedence is 1) environment `BAUPLAN_CONFIG_PATH` 2) ~/.bauplan/config.yml
        feature_flags: A dictionary of feature flags to enable or disable during the use of this client instance.

    """

    def __init__(
        self,
        profile: Optional[str] = None,
        api_key: Optional[str] = None,
        branch: Optional[str] = None,
        namespace: Optional[str] = None,
        cache: Optional[Literal['on', 'off']] = None,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        api_endpoint: Optional[str] = None,
        catalog_endpoint: Optional[str] = None,
        itersize: Optional[int] = None,
        client_timeout: Optional[int] = None,
        env: Optional[str] = None,
        config_file_path: Optional[Union[str, Path]] = None,
        feature_flags: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            profile=Profile.load_profile(
                profile=profile,
                api_key=api_key,
                branch=branch,
                namespace=namespace,
                cache=cache,
                debug=debug,
                verbose=verbose,
                args=args,
                api_endpoint=api_endpoint,
                catalog_endpoint=catalog_endpoint,
                client_timeout=client_timeout,
                itersize=itersize,
                env=env,
                config_file_path=config_file_path,
                feature_flags=feature_flags,
            ),
        )

        # instantiate interfaces to authenticated modules
        self._query = _Query(self.profile)
        self._run = _Run(self.profile)
        self._table_create = _TableCreate(self.profile)
        self._table_import = _TableImport(self.profile)
        self._external_table_create = _ExternalTableCreate(self.profile)
        self._info = _Info(self.profile)
        self._jobs = _Jobs(self.profile)

    # Run

    def run(
        self,
        project_dir: Optional[str] = None,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        parameters: Optional[Dict[str, Optional[Union[str, int, float, bool]]]] = None,
        cache: Optional[Literal['on', 'off']] = None,
        transaction: Optional[Literal['on', 'off']] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[Literal['on', 'off']] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        detach: bool = False,
    ) -> RunState:
        """
        Run a Bauplan project and return the state of the run. This is the equivalent of
        running through the CLI the `bauplan run` command. All parameters default to 'off'/false unless otherwise specified.

        ## Examples

        ```python notest
        # Run a daily sales pipeline on a dev branch, and if successful and data is good, merge to main
        run_state = client.run(
            project_dir='./etl_pipelines/daily_sales',
            ref="username.dev_branch",
            namespace='sales_analytics',
        )

        if str(run_state.job_status).lower() != "success":
            raise Exception(f"{run_state.job_id} failed: {run_state.job_status}")
        ```

        Parameters:
            project_dir: The directory of the project (where the `bauplan_project.yml` or `bauplan_project.yaml` file is located).
            ref: The ref, branch name or tag name from which to run the project.
            namespace: The Namespace to run the job in. If not set, the job will be run in the default namespace.
            parameters: Parameters for templating into SQL or Python models.
            cache: Whether to enable or disable caching for the run. Defaults to 'on'.
            transaction: Whether to enable or disable transaction mode for the run. Defaults to 'on'.
            dry_run: Whether to enable or disable dry-run mode for the run; models are not materialized.
            strict: Whether to enable or disable strict schema validation.
            preview: Whether to enable or disable preview mode for the run.
            debug: Whether to enable or disable debug mode for the run.
            args: Additional arguments (optional).
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode for the run.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
            detach: Whether to detach the run and return immediately instead of blocking on log streaming.
        Returns:
            `bauplan.state.RunState`: The state of the run.

        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._run.run(
                project_dir=project_dir,
                ref=ref_value,
                namespace=namespace_name,
                parameters=parameters,
                cache=cache,
                transaction=transaction,
                dry_run=dry_run,
                strict=strict,
                preview=preview,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
                detach=detach,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def rerun(
        self,
        job_id: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        cache: Optional[Literal['on', 'off']] = None,
        transaction: Optional[Literal['on', 'off']] = None,
        dry_run: Optional[bool] = None,
        strict: Optional[Literal['on', 'off']] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> ReRunState:
        """
        Re run a Bauplan job using its ID and return the state of the run.
        All on and off / bool parameters default to 'off' unless otherwise specified.

        ## Examples

        ```python notest
        rerun_state = client.rerun(
            job_id=prod_job_id,
            ref='feature-branch',
            cache='off'
        )

        # Check if rerun succeeded (best practice)
        if str(rerun_state.job_status).lower() != "success":
            raise Exception(f"Rerun failed with status: {rerun_state.job_status}")
        ```

        Parameters:
            job_id: The Job ID of the previous run. This can be used to re-run a previous run, e.g., on a different branch.
            ref: The ref, branch name or tag name from which to rerun the project.
            namespace: The Namespace to run the job in. If not set, the job will be run in the default namespace.
            cache: Whether to enable or disable caching for the run. Defaults to 'on'.
            transaction: Whether to enable or disable transaction mode for the run. Defaults to 'on'.
            dry_run: Whether to enable or disable dry-run mode for the run; models are not materialized.
            strict: Whether to enable or disable strict schema validation.
            preview: Whether to enable or disable preview mode for the run.
            debug: Whether to enable or disable debug mode for the run.
            args: Additional arguments (optional).
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode for the run.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            `bauplan.state.ReRunState`: The state of the run.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._run.rerun(
                job_id=job_id,
                ref=ref_value,
                namespace=namespace_name,
                cache=cache,
                transaction=transaction,
                dry_run=dry_run,
                strict=strict,
                preview=preview,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Query

    def query(
        self,
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> pa.Table:
        """
        Execute a SQL query and return the results as a pyarrow.Table.
        Note that this function uses Arrow also internally, resulting
        in a fast data transfer.

        If you prefer to return the results as a pandas DataFrame, use
        the `to_pandas` function of pyarrow.Table.

        ```python fixture:my_branch
        import bauplan

        client = bauplan.Client()

        # query the table and return result set as an arrow Table
        my_table = client.query(
            query='SELECT avg(age) as average_age FROM bauplan.titanic',
            ref='my_ref_or_branch_name',
        )

        # efficiently cast the table to a pandas DataFrame
        df = my_table.to_pandas()
        ```

        Parameters:
            query: The Bauplan query to execute.
            ref: The ref, branch name or tag name to query from.
            max_rows: The maximum number of rows to return; default: `None` (no limit).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            args: Additional arguments to pass to the query (default: None).
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode for the query.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The query results as a `pyarrow.Table`.

        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query(
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_generator(
        self,
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        as_json: Optional[bool] = False,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Execute a SQL query and return the results as a generator, where each row is
        a Python dictionary.

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # query the table and iterate through the results one row at a time
        res = client.query_to_generator(
            query='SELECT name, age FROM bauplan.titanic LIMIT 100',
            ref='my_ref_or_branch_name',
        )

        for row in res:
            ... # handle results
        ```

        Parameters:
            query: The Bauplan query to execute.
            ref: The ref, branch name or tag name to query from.
            max_rows: The maximum number of rows to return; default: `None` (no limit).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            as_json: Whether to return the results as a JSON-compatible string (default: `False`).
            args: Additional arguments to pass to the query (default: `None`).
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode for the query.
            client_timeout: seconds to timeout; this also cancels the remote job execution.

        Yields:
            A dictionary representing a row of query results.
        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_generator(
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                as_json=as_json,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_parquet_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> Path:
        """
        Export the results of a SQL query to a file in Parquet format.

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # query the table and iterate through the results one row at a time
        client.query_to_parquet_file(
            path='/tmp/out.parquet',
            query='SELECT name, age FROM bauplan.titanic LIMIT 100',
            ref='my_ref_or_branch_name',
        )
        ```

        Parameters:
            path: The name or path of the file parquet to write the results to.
            query: The Bauplan query to execute.
            ref: The ref, branch name or tag name to query from.
            max_rows: The maximum number of rows to return; default: `None` (no limit).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            args: Additional arguments to pass to the query (default: None).
            verbose: Whether to enable or disable verbose mode for the query.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The path of the file written.

        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_parquet_file(
                path=path,
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_csv_file(
        self,
        path: Union[str, Path],
        query: str,
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> Path:
        """
        Export the results of a SQL query to a file in CSV format.

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # query the table and iterate through the results one row at a time
        client.query_to_csv_file(
            path='/tmp/out.csv',
            query='SELECT name, age FROM bauplan.titanic LIMIT 100',
            ref='my_ref_or_branch_name',
        )
        ```

        Parameters:
            path: The name or path of the file csv to write the results to.
            query: The Bauplan query to execute.
            ref: The ref, branch name or tag name to query from.
            max_rows: The maximum number of rows to return; default: `None` (no limit).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            args: Additional arguments to pass to the query (default: None).
            verbose: Whether to enable or disable verbose mode for the query.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The path of the file written.

        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_csv_file(
                path=path,
                query=query,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def query_to_json_file(
        self,
        path: Union[str, Path],
        query: str,
        file_format: Optional[Literal['json', 'jsonl']] = 'json',
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        max_rows: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Path:
        """
        Export the results of a SQL query to a file in JSON format.

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # query the table and iterate through the results one row at a time
        client.query_to_json_file(
            path='/tmp/out.json',
            query='SELECT name, age FROM bauplan.titanic LIMIT 100',
            ref='my_ref_or_branch_name',
        )
        ```

        Parameters:
            path: The name or path of the file json to write the results to.
            query: The Bauplan query to execute.
            file_format: The format to write the results in; default: `json`. Allowed values are 'json' and 'jsonl'.
            ref: The ref, branch name or tag name to query from.
            max_rows: The maximum number of rows to return; default: `None` (no limit).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the query in. If not set, the query will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            args: Additional arguments to pass to the query (default: None).
            verbose: Whether to enable or disable verbose mode for the query.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The path of the file written.

        """
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.query_to_json_file(
                path=path,
                query=query,
                file_format=file_format,
                ref=ref_value,
                max_rows=max_rows,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def create_table(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        partitioned_by: Optional[str] = None,
        replace: Optional[bool] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> Table:
        """
        Create a table from an S3 location.

        This operation will attempt to create a table based of schemas of N
        parquet files found by a given search uri. This is a two step operation using
        `plan_table_creation ` and  `apply_table_creation_plan`.

        ```python notest
        import bauplan
        client = bauplan.Client()

        table = client.create_table(
            table='my_table_name',
            search_uri='s3://path/to/my/files/*.parquet',
            branch='my_branch_name',
        )
        ```

        Parameters:
            table: The table which will be created.
            search_uri: The location of the files to scan for schema.
            branch: The branch name in which to create the table in.
            namespace: Optional argument specifying the namespace. If not specified, it will be inferred based on table location or the default.
            partitioned_by: Optional argument specifying the table partitioning.
            replace: Replace the table if it already exists.
            debug: Whether to enable or disable debug mode for the query.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            Table

        Raises:
            TableCreatePlanStatusError: if the table creation plan fails.
            TableCreatePlanApplyStatusError: if the table creation plan apply fails.

        """
        table_create_plan = self.plan_table_creation(
            table=table,
            search_uri=search_uri,
            branch=branch,
            namespace=namespace,
            partitioned_by=partitioned_by,
            replace=replace,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
        )
        _ = self.apply_table_creation_plan(
            plan=table_create_plan,
            debug=debug,
            args=args,
            priority=priority,
            verbose=verbose,
            client_timeout=client_timeout,
        )

        # The namespace has been resolved by the commander
        parts = table_create_plan.ctx.table_name.split('.')
        if len(parts) > 1:
            return Table(
                name=parts[-1],
                namespace='.'.join(parts[:-1]),
            )

        return Table(
            name=table_create_plan.ctx.table_name,
            namespace=table_create_plan.ctx.namespace,
        )

    def plan_table_creation(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        partitioned_by: Optional[str] = None,
        replace: Optional[bool] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> TableCreatePlanState:
        """
        Create a table import plan from an S3 location.

        This operation will attempt to create a table based of schemas of N
        parquet files found by a given search uri. A YAML file containing the
        schema and plan is returns and if there are no conflicts, it is
        automatically applied.

        ```python notest
        import bauplan
        client = bauplan.Client()

        plan_state = client.plan_table_creation(
            table='my_table_name',
            search_uri='s3://path/to/my/files/*.parquet',
            branch='my_branch_name',
        )
        if plan_state.error:
            plan_error_action(...)
        success_action(plan_state.plan)
        ```

        Parameters:
            table: The table which will be created.
            search_uri: The location of the files to scan for schema.
            branch: The branch name in which to create the table in.
            namespace: Optional argument specifying the namespace. If not specified, it will be inferred based on table location or the default.
            partitioned_by: Optional argument specifying the table partitioning.
            replace: Replace the table if it already exists.
            debug: Whether to enable or disable debug mode.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode.
            client_timeout: seconds to timeout; this also cancels the remote job execution.

        Returns:
            The plan state.

        Raises:
            TableCreatePlanStatusError: if the table creation plan fails.
        """
        branch_name = _Validate.optional_branch_name('branch', branch)
        table_name = _Validate.table_name('table', table)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._table_create.plan(
                table_name=table_name,
                search_uri=search_uri,
                branch_name=branch_name,
                namespace=namespace_name,
                partitioned_by=partitioned_by,
                replace=replace,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def apply_table_creation_plan(
        self,
        plan: Union[Dict, TableCreatePlanState],
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
    ) -> TableCreatePlanApplyState:
        """
        Apply a plan for creating a table. It is done automaticaly during th
        table plan creation if no schema conflicts exist. Otherwise, if schema
        conflicts exist, then this function is used to apply them after the
        schema conflicts are resolved. Most common schema conflict is a two
        parquet files with the same column name but different datatype

        Parameters:
            plan: The plan to apply.
            debug: Whether to enable or disable debug mode for the query.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The plan state.

        Raises:
            TableCreatePlanApplyStatusError: if the table creation plan apply fails.


        """
        try:
            return self._table_create.apply(
                plan=plan,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def import_data(
        self,
        table: Union[str, Table],
        search_uri: str,
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        continue_on_error: bool = False,
        import_duplicate_files: bool = False,
        best_effort: bool = False,
        # transformation_query: Optional[str] = None,
        preview: Optional[Union[Literal['on', 'off', 'head', 'tail'], str]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        detach: bool = False,
    ) -> TableDataImportState:
        """
        Imports data into an already existing table.

        ```python notest
        import bauplan
        client = bauplan.Client()

        plan_state = client.import_data(
            table='my_table_name',
            search_uri='s3://path/to/my/files/*.parquet',
            branch='my_branch_name',
        )
        if plan_state.error:
            plan_error_action(...)
        success_action(plan_state.plan)
        ```

        Parameters:
            table: Previously created table in into which data will be imported.
            search_uri: Uri which to scan for files to import.
            branch: Branch in which to import the table.
            namespace: Namespace of the table. If not specified, namespace will be infered from table name or default settings.
            continue_on_error: Do not fail the import even if 1 data import fails.
            import_duplicate_files: Ignore prevention of importing s3 files that were already imported.
            best_effort: Don't fail if schema of table does not match.
            preview: Whether to enable or disable preview mode for the import.
            debug: Whether to enable or disable debug mode for the import.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
            detach: Whether to detach the job and return immediately without waiting for the job to finish.
        Returns:
            A `bauplan.state.TableDataImportState` object.

        """
        table_name = _Validate.table_name('table', table)
        branch_name = _Validate.optional_branch_name('branch', branch)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._table_import.data_import(
                table_name=table_name,
                search_uri=search_uri,
                branch_name=branch_name,
                namespace=namespace_name,
                continue_on_error=continue_on_error,
                import_duplicate_files=import_duplicate_files,
                best_effort=best_effort,
                transformation_query=None,
                preview=preview,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
                detach=detach,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    def create_external_table_from_parquet(
        self,
        table: Union[str, Table],
        search_patterns: List[str],
        *,  # From here only keyword arguments are allowed
        branch: Optional[Union[str, Branch]] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        overwrite: bool = False,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        detach: bool = False,
    ) -> ExternalTableCreateState:
        """
        Creates an external table from S3 files.

        ```python notest
        import bauplan
        client = bauplan.Client()

        # Create from S3 files
        state = client.create_external_table_from_parquet(
            table='my_external_table',
            search_patterns=['s3://path1/to/my/files/*.parquet', 's3://path2/to/my/file/f1.parquet'],
            branch='my_branch_name',
        )

        if state.error:
            handle_error(state.error)
        else:
            print(f"External table created: {state.ctx.table_name}")
        ```

        Parameters:
            table: The name of the external table to create.
            search_patterns: List of search_patterns for files to create the external table from. Must resolve to parquet files
            branch: Branch in which to create the table.
            namespace: Namespace of the table. If not specified, namespace will be inferred from table name or default settings.
            overwrite: Whether to delete and recreate the table if it already exists.
            debug: Whether to enable or disable debug mode for the operation.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            verbose: Whether to enable or disable verbose mode.
            client_timeout: seconds to timeout; this also cancels the remote job execution.
            detach: Whether to detach the job and return immediately without waiting for the job to finish.

        Returns:
            The external table create state.
        """
        table_name = _Validate.table_name('table', table)
        branch_name = _Validate.optional_branch_name('branch', branch)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace)
        try:
            return self._external_table_create.create_external_table_from_parquet(
                table_name=table_name,
                search_patterns=search_patterns,
                branch_name=branch_name,
                namespace=namespace_name,
                overwrite=overwrite,
                debug=debug,
                args=args,
                priority=priority,
                verbose=verbose,
                client_timeout=client_timeout,
                detach=detach,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Scan

    def scan(
        self,
        table: Union[str, Table],
        ref: Optional[Union[str, Branch, Tag, Ref]] = None,
        columns: Optional[List[str]] = None,
        filters: Optional[str] = None,
        limit: Optional[int] = None,
        cache: Optional[Literal['on', 'off']] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        debug: Optional[bool] = None,
        args: Optional[Dict[str, str]] = None,
        priority: Optional[int] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> pa.Table:
        """
        Execute a table scan (with optional filters) and return the results as an arrow Table.

        Note that this function uses SQLGlot to compose a safe SQL query,
        and then internally defer to the query_to_arrow function for the actual
        scan.
        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # run a table scan over the data lake
        # filters are passed as a string
        my_table = client.scan(
            table='titanic',
            ref='my_ref_or_branch_name',
            namespace='bauplan',
            columns=['name'],
            filters='age < 30',
        )
        ```

        Parameters:
            table: The table to scan.
            ref: The ref, branch name or tag name to scan from.
            columns: The columns to return (default: `None`).
            filters: The filters to apply (default: `None`).
            limit: The maximum number of rows to return (default: `None`).
            cache: Whether to enable or disable caching for the query.
            connector: The connector type for the model (defaults to Bauplan). Allowed values are 'snowflake' and 'dremio'.
            connector_config_key: The key name if the SSM key is custom with the pattern `bauplan/connectors/<connector_type>/<key>`.
            connector_config_uri: Full SSM uri if completely custom path, e.g. `ssm://us-west-2/123456789012/baubau/dremio`.
            namespace: The Namespace to run the scan in. If not set, the scan will be run in the default namespace for your account.
            debug: Whether to enable or disable debug mode for the query.
            args: dict of arbitrary args to pass to the backend.
            priority: Optional job priority (1-10, where 10 is highest priority).
            client_timeout: seconds to timeout; this also cancels the remote job execution.
        Returns:
            The scan results as a `pyarrow.Table`.

        """
        table_name = _Validate.table_name('table', table)
        ref_value = _Validate.optional_ref('ref', ref)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        try:
            return self._query.scan(
                table_name=table_name,
                ref=ref_value,
                columns=columns,
                filters=filters,
                limit=limit,
                cache=cache,
                connector=connector,
                connector_config_key=connector_config_key,
                connector_config_uri=connector_config_uri,
                namespace=namespace_name,
                debug=debug,
                args=args,
                priority=priority,
                client_timeout=client_timeout,
                **kwargs,
            )
        except grpc._channel._InactiveRpcError as e:
            if hasattr(e, 'details'):
                raise exceptions.JobError(e.details()) from e
            raise exceptions.JobError(e) from e

    # Catalog

    def get_branches(
        self,
        name: Optional[str] = None,
        user: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetBranchesResponse:
        """
        Get the available data branches in the Bauplan catalog.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python
        import bauplan
        client = bauplan.Client()

        for branch in client.get_branches():
            ...
        ```

        Parameters:
            name: Filter the branches by name.
            user: Filter the branches by user.
            limit: Optional, max number of branches to get.
        Returns:
            A `bauplan.schema.GetBranchesResponse` object.

        """
        params = {
            'filter_by_name': _Validate.optional_string('name', name),
            'filter_by_user': _Validate.optional_string('user', user),
        }
        limit = _Validate.optional_positive_int('limit', limit)

        return GetBranchesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                method=Constants.HTTP_METHOD_GET,
                path=['v0', 'branches'],
                params=params,
            ),
            data_mapper=Branch.model_validate,
            limit=limit,
            itersize=self.profile.itersize,
        )

    def get_branch(
        self,
        branch: Union[str, Branch],
    ) -> Branch:
        """
        Get the branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        # retrieve only the tables as tuples of (name, kind)
        branch = client.get_branch('my_branch_name')
        ```

        Parameters:
            branch: The name of the branch to retrieve.
        Returns:
            A `Branch` object.

        Raises:
            BranchNotFoundError: if the branch does not exist.
            NotABranchRefError: if the object is not a branch.
            ForbiddenError: if the user does not have access to the branch.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        branch_name = _Validate.branch_name('branch', branch)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_GET,
            path=['v0', 'branches', branch_name],
        )
        return Branch.model_validate(out.data)

    def has_branch(
        self,
        branch: Union[str, Branch],
    ) -> bool:
        """
        Check if a branch exists.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        if client.has_branch('my_branch_name')
            # do something
        ```

        Parameters:
            branch: The name of the branch to check.
        Returns:
            A boolean for if the branch exists.

        Raises:
            NotABranchRefError: if the object is not a branch.
            ForbiddenError: if the user does not have access to the branch.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        try:
            self.get_branch(branch=branch)
            return True
        except exceptions.BranchNotFoundError:
            return False

    def create_branch(
        self,
        branch: Union[str, Branch],
        from_ref: Union[str, Branch, Tag],
        *,  # From here only keyword arguments are allowed
        if_not_exists: bool = False,
    ) -> Branch:
        """
        Create a new branch at a given ref.
        The branch name should follow the convention of `username.branch_name`,
        otherwise non-admin users won't be able to complete the operation.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan

        client = bauplan.Client()
        username = client.info().user.username

        branch = client.create_branch(
            branch = username+'.feature_branch',
            from_ref = 'branch_name@hash',
            if_not_exists = True,
        )
        ```

        Parameters:
            branch: The name of the new branch.
            from_ref: The name of the base branch; either a branch like "main" or ref like "main@[sha]".
            if_not_exists: If set to `True`, the branch will not be created if it already exists.
        Returns:
            The created branch object.

        Raises:
            CreateBranchForbiddenError: if the user does not have access to create the branch.
            BranchExistsError: if the branch already exists.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.
        """
        branch_name = _Validate.branch_name('branch', branch)
        from_ref = _Validate.ref('from_ref', from_ref)
        if_not_exists = _Validate.boolean('if_not_exists', if_not_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.BranchExistsError,
            condition=if_not_exists,
            handler=lambda e: e.context_ref,
        ) as h:
            out = self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_POST,
                path=['v0', 'branches'],
                body={
                    'branch_name': branch_name,
                    'from_ref': from_ref,
                },
            )
            return Branch.model_validate(out.data)

        return h.value

    def rename_branch(
        self,
        branch: Union[str, Branch],
        new_branch: Union[str, Branch],
    ) -> Branch:
        """
        Rename an existing branch.
        The branch name should follow the convention of "username.branch_name",
        otherwise non-admin users won't be able to complete the operation.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.rename_branch(
            branch='username.old_name',
            new_branch='username.new_name',
        )
        ```

        Parameters:
            branch: The name of the branch to rename.
            new_branch: The name of the new branch.
        Returns:
            The renamed `Branch` object.

        Raises:
            `RenameBranchForbiddenError`: if the user does not have access to create the branch.
            `UnauthorizedError`: if the user's credentials are invalid.
            `ValueError`: if one or more parameters are invalid.

        """
        branch_name = _Validate.branch_name('branch', branch)
        new_branch_name = _Validate.branch_name('new_branch', new_branch)

        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_PATCH,
            path=['v0', 'branches', branch_name],
            body={'branch_name': new_branch_name},
        )
        return Branch.model_validate(out.data)

    def merge_branch(
        self,
        source_ref: Union[str, Branch, Tag],
        into_branch: Union[str, Branch],
        commit_message: Optional[str] = None,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        message: Optional[str] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Merge one branch into another.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.merge_branch(
            source_ref='my_ref_or_branch_name',
            into_branch='main',
        )
        ```

        Parameters:
            source_ref: The name of the merge source; either a branch like "main" or ref like "main@[sha]".
            into_branch: The name of the merge target.
            commit_message: Optional, the commit message.
            commit_body: Optional, the commit body.
            commit_properties: Optional, a list of properties to attach to the merge.
        Returns:
            the `Branch` where the merge was made.

        Raises:
            MergeForbiddenError: if the user does not have access to merge the branch.
            BranchNotFoundError: if the destination branch does not exist.
            NotAWriteBranchError: if the destination branch is not a writable ref.
            MergeConflictError: if the merge operation results in a conflict.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        into_branch_name = _Validate.branch_name('into_branch', into_branch)
        source_ref_value = _Validate.ref('source_ref', source_ref)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_POST,
            path=['v0', 'refs', source_ref_value, 'merge', into_branch_name],
            body={
                'commit_message': _Validate.optional_string('commit_message', commit_message or message),
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties(
                    'commit_properties', commit_properties or properties
                ),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def delete_branch(
        self,
        branch: Union[str, Branch],
        *,  # From here only keyword arguments are allowed
        if_exists: bool = False,
    ) -> bool:
        """
        Delete a branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        if client.delete_branch('my_branch_name')
            #do something
        ```

        Parameters:
            branch: The name of the branch to delete.
            if_exists: If set to `True`, the branch will not raise an error if it does not exist.
        Returns:
            A boolean for if the branch was deleted.

        Raises:
            DeleteBranchForbiddenError: if the user does not have access to delete the branch.
            BranchNotFoundError: if the branch does not exist.
            BranchHeadChangedError: if the branch head hash has changed.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        branch_name = _Validate.branch_name('branch', branch)
        if_exists = _Validate.boolean('if_exists', if_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.BranchNotFoundError,
            condition=if_exists,
            handler=lambda e: False,
        ) as h:
            self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_DELETE,
                path=['v0', 'branches', branch_name],
            )
            return True

        return h.value

    def get_namespaces(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetNamespacesResponse:
        """
        Get the available data namespaces in the Bauplan catalog branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_namespace
        import bauplan
        client = bauplan.Client()

        for namespace in client.get_namespaces('my_ref_or_branch_name'):
            ...
        ```

        Parameters:
            ref: The ref, branch name or tag name to retrieve the namespaces from.
            filter_by_name: Optional, filter the namespaces by name.
            limit: Optional, max number of namespaces to get.

        Raises:
            RefNotFoundError: if the ref does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        Yields:
            A Namespace object.

        """
        ref_value = _Validate.ref('ref', ref)
        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
        }
        limit = _Validate.optional_positive_int('limit', limit)

        return GetNamespacesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                method=Constants.HTTP_METHOD_GET,
                path=['v0', 'refs', ref_value, 'namespaces'],
                params=params,
            ),
            data_mapper=Namespace.model_validate,
            limit=limit,
            itersize=self.profile.itersize,
        )

    def get_namespace(
        self,
        namespace: Union[str, Namespace],
        ref: Union[str, Branch, Tag, Ref],
    ) -> Namespace:
        """
        Get a namespace.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_namespace
        import bauplan
        client = bauplan.Client()

        namespace =  client.get_namespace(
            namespace='my_namespace_name',
            ref='my_branch_name',
        )
        ```

        Parameters:
            namespace: The name of the namespace to get.
            ref: The ref, branch name or tag name to check the namespace on.
        Returns:
            A `bauplan.schema.Namespace` object.

        Raises:
            NamespaceNotFoundError: if the namespace does not exist.
            RefNotFoundError: if the ref does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        ref_value = _Validate.ref('ref', ref)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_GET,
            path=['v0', 'refs', ref_value, 'namespaces', namespace_name],
        )
        return Namespace.model_validate({**out.data, 'ref': out.ref})

    def create_namespace(
        self,
        namespace: Union[str, Namespace],
        branch: Union[str, Branch],
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        *,  # From here only keyword arguments are allowed
        if_not_exists: bool = False,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Namespace:
        """
        Create a new namespace at a given branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        assert client.create_namespace(
            namespace='my_namespace_name',
            branch='my_branch_name',
            properties={'k1': 'v1', 'k2': 'v2'},
            if_not_exists=True,
        )
        ```

        Parameters:
            namespace: The name of the namespace.
            branch: The name of the branch to create the namespace on.
            commit_body: Optional, the commit body to attach to the operation.
            commit_properties: Optional, a list of properties to attach to the commit.
            if_not_exists: If set to `True`, the namespace will not be created if it already exists.
        Returns:
            The created `bauplan.schema.Namespace` object.

        Raises:
            CreateNamespaceForbiddenError: if the user does not have access to create the namespace.
            BranchNotFoundError: if the branch does not exist.
            NotAWriteBranchError: if the destination branch is not a writable ref.
            BranchHeadChangedError: if the branch head hash has changed.
            NamespaceExistsError: if the namespace already exists.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        branch_name = _Validate.branch_name('branch', branch)
        if_not_exists = _Validate.boolean('if_not_exists', if_not_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.NamespaceExistsError,
            condition=if_not_exists,
            handler=lambda e: e.context_namespace,
        ) as h:
            out = self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_POST,
                path=['v0', 'branches', branch_name, 'namespaces'],
                body={
                    'namespace_name': namespace_name,
                    'commit_body': _Validate.optional_string('commit_body', commit_body),
                    'commit_properties': _Validate.optional_properties(
                        'commit_properties', commit_properties or properties
                    ),
                },
            )
            return Namespace.model_validate({**out.data, 'ref': out.ref})

        return h.value

    def delete_namespace(
        self,
        namespace: Union[str, Namespace],
        branch: Union[str, Branch],
        *,  # From here only keyword arguments are allowed
        if_exists: bool = False,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Delete a namespace.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch fixture:my_namespace
        import bauplan
        client = bauplan.Client()

        assert client.delete_namespace(
            namespace='my_namespace_name',
            branch='my_branch_name',
        )
        ```

        Parameters:
            namespace: The name of the namespace to delete.
            branch: The name of the branch to delete the namespace from.
            commit_body: Optional, the commit body to attach to the operation.
            commit_properties: Optional, a list of properties to attach to the commit.
            if_exists: If set to `True`, the namespace will not be deleted if it does not exist.
        Returns:
            A `bauplan.schema.Branch` object pointing to head.

        Raises:
            DeleteBranchForbiddenError: if the user does not have access to delete the branch.
            BranchNotFoundError: if the branch does not exist.
            NotAWriteBranchError: if the destination branch is not a writable ref.
            BranchHeadChangedError: if the branch head hash has changed.
            NamespaceNotFoundError: if the namespace does not exist.
            NamespaceIsNotEmptyError: if the namespace is not empty.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        namespace_name = _Validate.namespace_name('namespace', namespace)
        branch_name = _Validate.branch_name('branch', branch)
        if_exists = _Validate.boolean('if_exists', if_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.NamespaceNotFoundError,
            condition=if_exists,
            handler=lambda e: cast(Branch, e.context_ref),
        ) as h:
            out = self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_DELETE,
                path=['v0', 'branches', branch_name, 'namespaces', namespace_name],
                body={
                    'commit_properties': _Validate.optional_properties(
                        'properties', commit_properties or properties
                    ),
                    'commit_body': _Validate.optional_string('commit_body', commit_body),
                },
            )
            assert out.ref is not None
            return Branch(**out.ref.model_dump())

        return h.value

    def has_namespace(
        self,
        namespace: Union[str, Namespace],
        ref: Union[str, Branch, Tag, Ref],
    ) -> bool:
        """
        Check if a namespace exists.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_namespace
        import bauplan
        client = bauplan.Client()

        assert client.has_namespace(
            namespace='my_namespace_name',
            ref='my_branch_name',
        )
        ```

        Parameters:
            namespace: The name of the namespace to check.
            ref: The ref, branch name or tag name to check the namespace on.

        Returns:
            A boolean for if the namespace exists.

        Raises:
            RefNotFoundError: if the ref does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        try:
            self.get_namespace(namespace=namespace, ref=ref)
            return True
        except exceptions.ResourceNotFoundError:
            return False

    def get_job(self, job_id: str) -> Job:
        """
        EXPERIMENTAL: Get a job by ID or ID prefix.

        Parameters:
            job_id: A job ID

        """
        job_id = _Validate.string('job_id', job_id)

        return self._jobs.get_job(job_id)

    def list_jobs(
        self,
        all_users: Optional[bool] = None,
        *,  # From here only keyword arguments are allowed
        filter_by_id: Optional[str] = None,
        filter_by_status: Optional[Union[str, JobState]] = None,
        filter_by_finish_time: Optional[DateRange] = None,
    ) -> List[Job]:
        """
        DEPRECATED: List all jobs

        Parameters:
            all_users: Optional[bool]:  (Default value = None)
            filter_by_id: Optional[str]:  (Default value = None)
            filter_by_status: Optional[Union[str, JobState]]:  (Default value = None)
            filter_by_finish_time: Optional[DateRange]:  (Default value = None)

        A DateRange is an alias for `tuple[Optional[datetime], Optional[datetime]]`, where the
        first element is an "after" (start) filter and the second element is a "before" (end)
        filter.

        The `filter_by_finish_time` parameter takes a DateRange and allows jobs with a finish time
        later than "after" (if specified) and a finish time earlier than "before" (if specified),
        or between both. If neither is specified, for example `(None, None)`, then the behavior is
        the same as not specifying the filter itself, for example `filter_by_finish_time=None`.
        """

        return self.get_jobs(
            all_users=all_users,
            filter_by_ids=[filter_by_id] if filter_by_id else None,
            filter_by_statuses=filter_by_status,
            filter_by_created_after=filter_by_finish_time[0] if filter_by_finish_time else None,
            filter_by_created_before=filter_by_finish_time[1] if filter_by_finish_time else None,
            limit=self.profile.itersize,
        ).values()

    def get_jobs(
        self,
        *,  # From here only keyword arguments are allowed
        all_users: Optional[bool] = None,
        filter_by_ids: Optional[Union[str, List[str]]] = None,
        filter_by_users: Optional[Union[str, List[str]]] = None,
        filter_by_kinds: Optional[Union[str, JobKind, List[Union[str, JobKind]]]] = None,
        filter_by_statuses: Optional[Union[str, JobState, List[Union[str, JobState]]]] = None,
        filter_by_created_after: Optional[datetime] = None,
        filter_by_created_before: Optional[datetime] = None,
        limit: Optional[int] = 500,
    ) -> ListJobsResponse:
        """
        Get jobs with optional filtering.

        Parameters:
            all_users: Optional[bool]: Whether to list jobs from all users or only the current user.
            filter_by_ids: Optional[Union[str, List[str]]]: Optional, filter by job IDs.
            filter_by_users: Optional[Union[str, List[str]]]: Optional, filter by job users.
            filter_by_kinds: Optional[Union[str, JobKind, List[Union[str, JobKind]]]]: Optional, filter by job kinds.
            filter_by_statuses: Optional[Union[str, JobState, List[Union[str, JobState]]]]: Optional, filter by job statuses.
            filter_by_created_after: Optional[datetime]: Optional, filter jobs created after this datetime.
            filter_by_created_before: Optional[datetime]: Optional, filter jobs created before this datetime.
            limit: Optional[int]: Optional, max number of jobs to return.

        Returns:
            A `bauplan.schema.ListJobsResponse` object.

        """
        filter_by_ids = _Validate.optional_string_list('filter_by_ids', filter_by_ids)
        filter_by_users = _Validate.optional_string_list('filter_by_users', filter_by_users)
        filter_by_kinds = _Validate.optional_pb_job_kinds('filter_by_kinds', filter_by_kinds)
        filter_by_statuses = _Validate.optional_pb_job_status_types('filter_by_statuses', filter_by_statuses)
        filter_by_created_after = _Validate.optional_pb_timestamp(
            'filter_by_created_after', filter_by_created_after
        )
        filter_by_created_before = _Validate.optional_pb_timestamp(
            'filter_by_created_before', filter_by_created_before
        )
        limit = _Validate.optional_positive_int('limit', limit)

        return self._jobs.get_jobs(
            # If one or more user filters are set, we override all_users to True
            all_users=True if filter_by_users else all_users,
            filter_by_ids=filter_by_ids,
            filter_by_users=filter_by_users,
            filter_by_kinds=filter_by_kinds,
            filter_by_statuses=filter_by_statuses,
            filter_by_created_after=filter_by_created_after,
            filter_by_created_before=filter_by_created_before,
            limit=limit or 500,  # None is not accepted here, defaulting to 500
            itersize=self.profile.itersize,
        )

    def get_job_logs(self, job_id_prefix: str = '', job: Union[str, Job] = '') -> List[JobLog]:
        """
        EXPERIMENTAL: Get logs for a job by ID prefix or from a specified `Job`.

        Parameters:
            job: Union[str, Job]: A job ID, prefix of a job ID, a Job instance.
            job_id_prefix: str: The prefix of a Job ID (deprecated in favor of `job`).

        """

        # For backwards compatibility, we don't yet remove job_id_prefix.
        # Which means we need to check at runtime that at least one is set.
        if not job_id_prefix and not job:
            raise ParameterMissingRequiredValuesError(['job', 'job_id_prefix'])

        # Cascade through the various approaches
        query_jobid = job_id_prefix

        if isinstance(job, Job):
            query_jobid = job.id

        elif isinstance(job, str) and job != '':
            query_jobid = job

        # TODO: it could be nicer to return an object with convenience methods
        #       instead of a list of (user-facing) log events
        job_log = self._jobs.get_logs(job=query_jobid)
        return job_log.log_events

    def get_job_context(
        self,
        job: Union[str, Job],
        *,  # From here only keyword arguments are allowed
        include_logs: bool = False,
        include_snapshot: bool = False,
    ) -> JobContext:
        """
        EXPERIMENTAL: Get logs for a job by ID prefix or from a specified `Job`.

        Parameters:
            job: Union[str, Job]: A job ID, prefix of a job ID, a Job instance.
            job_id_prefix: str: The prefix of a Job ID (deprecated in favor of `job`).

        """

        job_ids = [job if isinstance(job, str) else job.id]

        job_ctxs = self.get_job_contexts(
            jobs=job_ids,
            include_logs=include_logs,
            include_snapshot=include_snapshot,
        )

        if len(job_ctxs) > 1:
            if isinstance(job, Job):
                raise JobAmbiguousError(job.id)
            raise JobAmbiguousError(job)

        if len(job_ctxs) == 0:
            raise JobContextError(job_ids=job_ids)

        return job_ctxs[0]

    def get_job_contexts(
        self,
        jobs: Union[List[str], List[Job]],
        *,  # From here only keyword arguments are allowed
        include_logs: bool = False,
        include_snapshot: bool = False,
    ) -> List[JobContext]:
        """
        EXPERIMENTAL: Get logs for a job by ID prefix or from a specified `Job`.

        Parameters:
            job: Union[str, Job]: A job ID, prefix of a job ID, a Job instance.
            job_id_prefix: str: The prefix of a Job ID (deprecated in favor of `job`).

        """

        try:
            return self._jobs.get_contexts(
                jobs=jobs,
                include_logs=include_logs,
                include_snapshot=include_snapshot,
            )
        except JobContextError as jobctx_err:
            raise jobctx_err
        except Exception:
            job_id_list = [job if isinstance(job, str) else job.id for job in jobs]
            raise JobContextError(job_ids=job_id_list) from None

    def cancel_job(self, job_id: str) -> None:
        """
        EXPERIMENTAL: Cancel a job by ID.

        Parameters:
            job_id: A job ID

        """
        return self._jobs.cancel_job(job_id)

    def get_tables(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        filter_by_namespace: Optional[str] = None,
        namespace: Optional[Union[str, Namespace]] = None,
        include_raw: bool = False,
        limit: Optional[int] = None,
    ) -> GetTablesResponse:
        """
        Get the tables and views in the target branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        for table in client.get_tables('my_branch_name'):
            ...
        ```

        Parameters:
            ref: The ref or branch to get the tables from.
            filter_by_name: Optional, the table name to filter by.
            filter_by_namespace: Optional, the namespace to get filtered tables from.
            namespace: DEPRECATED: Optional, the namespace to get filtered tables from.
            include_raw: Whether or not to include the raw metadata.json object as a nested dict.
            limit: Optional, max number of tables to get.
        Returns:
            A `bauplan.schema.GetTablesResponse` object.

        """
        ref_value = _Validate.ref('ref', ref)
        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
            'filter_by_namespace': _Validate.optional_namespace_name(
                'filter_by_namespace', filter_by_namespace
            )
            or _Validate.optional_namespace_name('namespace', namespace),
            'raw': 1 if include_raw else 0,
        }
        limit = _Validate.optional_positive_int('limit', limit)
        return GetTablesResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                method=Constants.HTTP_METHOD_GET,
                path=['v0', 'refs', ref_value, 'tables'],
                params=params,
            ),
            data_mapper=TableWithMetadata.model_validate,
            limit=limit,
            itersize=self.profile.itersize,
        )

    def get_table(
        self,
        table: Union[str, Table],
        ref: Union[str, Branch, Tag, Ref],
        namespace: Optional[Union[str, Namespace]] = None,
        include_raw: bool = False,
    ) -> TableWithMetadata:
        """
        Get the table data and metadata for a table in the target branch.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch fixture:my_namespace
        import bauplan
        client = bauplan.Client()

        # get the fields and metadata for a table
        table = client.get_table(
            table='titanic',
            ref='my_ref_or_branch_name',
            namespace='bauplan',
        )

        # You can get the total number of rows this way.
        num_records = table.records

        # Or access the schema.
        for c in table.fields:
            ...
        ```

        Parameters:
            ref: The ref, branch name or tag name to get the table from.
            table: The table to retrieve.
            namespace: The namespace of the table to retrieve.
            include_raw: Whether or not to include the raw metadata.json object as a nested dict.
        Returns:
            a `bauplan.schema.TableWithMetadata` object, optionally including the raw `metadata.json` object.

        Raises:
            RefNotFoundError: if the ref does not exist.
            NamespaceNotFoundError: if the namespace does not exist.
            NamespaceConflictsError: if conflicting namespaces names are specified.
            TableNotFoundError: if the table does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        ref_value = _Validate.ref('ref', ref)
        table_name = _Validate.table_name('table', table)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_GET,
            path=['v0', 'refs', ref_value, 'tables', table_name],
            params={
                'raw': 1 if include_raw else 0,
                'namespace': namespace_name,
            },
        )
        return TableWithMetadata.model_validate(out.data)

    def has_table(
        self,
        table: Union[str, Table],
        ref: Union[str, Branch, Tag, Ref],
        namespace: Optional[Union[str, Namespace]] = None,
    ) -> bool:
        """
        Check if a table exists.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_branch
        import bauplan
        client = bauplan.Client()

        assert client.has_table(
            table='titanic',
            ref='my_ref_or_branch_name',
            namespace='bauplan',
        )
        ```

        Parameters:
            ref: The ref, branch name or tag name to get the table from.
            table: The table to retrieve.
            namespace: The namespace of the table to check.
        Returns:
            A boolean for if the table exists.

        Raises:
            RefNotFoundError: if the ref does not exist.
            NamespaceNotFoundError: if the namespace does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        try:
            self.get_table(table=table, ref=ref, namespace=namespace)
            return True
        except exceptions.TableNotFoundError:
            return False

    def delete_table(
        self,
        table: Union[str, Table],
        branch: Union[str, Branch],
        *,  # From here only keyword arguments are allowed
        namespace: Optional[Union[str, Namespace]] = None,
        if_exists: bool = False,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
        # TODO: TO DEPRECATE
        properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Drop a table.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.delete_table(
            table='my_table_name',
            branch='my_branch_name',
            namespace='my_namespace',
        )
        ```

        Parameters:
            table: The table to delete.
            branch: The branch on which the table is stored.
            namespace: The namespace of the table to delete.
            commit_body: Optional, the commit body message to attach to the commit.
            commit_properties: Optional, a list of properties to attach to the commit.
            if_exists: If set to `True`, the table will not raise an error if it does not exist.
        Returns:
            The deleted `bauplan.schema.Table` object.

        Raises:
            DeleteTableForbiddenError: if the user does not have access to delete the table.
            BranchNotFoundError: if the branch does not exist.
            NotAWriteBranchError: if the destination branch is not a writable ref.
            BranchHeadChangedError: if the branch head hash has changed.
            TableNotFoundError: if the table does not exist.
            NamespaceConflictsError: if conflicting namespaces names are specified.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        branch_name = _Validate.branch_name('branch', branch)
        table_name = _Validate.table_name('table', table)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        if_exists = _Validate.boolean('if_exists', if_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.TableNotFoundError,
            condition=if_exists,
            handler=lambda e: cast(Branch, e.context_ref),
        ) as h:
            out = self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_DELETE,
                path=['v0', 'branches', branch_name, 'tables', table_name],
                params={
                    'namespace': namespace_name,
                },
                body={
                    'commit_body': _Validate.optional_string('commit_body', commit_body),
                    'commit_properties': _Validate.optional_properties(
                        'commit_properties', commit_properties or properties
                    ),
                },
            )
            assert out.ref is not None
            return Branch(**out.ref.model_dump())

        return h.value

    def create_external_table_from_metadata(
        self,
        table: Union[str, Table],
        metadata_json_uri: str,
        *,  # From here only keyword arguments are allowed
        namespace: Optional[Union[str, Namespace]] = None,
        branch: Optional[Union[str, Branch]] = None,
        overwrite: bool = False,
    ) -> TableWithMetadata:
        """
        Create an external table from an Iceberg metadata.json file.

        This operation creates an external table by pointing to an existing Iceberg table's
        metadata.json file. This is useful for importing external Iceberg tables into Bauplan
        without copying the data.

        ```python notest
        import bauplan
        client = bauplan.Client()

        # Create an external table from metadata
        result = client.create_external_table_from_metadata(
            table='my_external_table',
            metadata_json_uri='s3://my-bucket/path/to/metadata/00001-abc123.metadata.json',
            namespace='my_namespace',
            branch='my_branch_name',
        )
        ```

        Parameters:
            table: The name of the table to create.
            metadata_json_uri: The S3 URI pointing to the Iceberg table's metadata.json file.
            namespace: The namespace for the table (required).
            branch: The branch name in which to create the table. Defaults to '-' if not specified.
            overwrite: Whether to overwrite an existing table with the same name (default: False).

        Returns:
            TableWithMetadata: The registered table with full metadata.

        Raises:
            ValueError: if metadata_json_uri is empty or invalid, or if table parameter is invalid.
            BranchNotFoundError: if the branch does not exist.
            NamespaceNotFoundError: if the namespace does not exist.
            UnauthorizedError: if the user's credentials are invalid.
            InvalidDataError: if the metadata location is within the warehouse directory.
            UpdateConflictError: if a table with the same name already exists and overwrite=False.
            BauplanError: for other API errors during registration or retrieval.

        """

        branch_name = _Validate.optional_branch_name('branch', branch) or '-'
        table_name = _Validate.table_name('table', table)
        ns_name = _Validate.optional_namespace_name('namespace', namespace, self.profile.namespace) or '-'

        metadata_json_uri = _Validate.string('metadata_json_uri', metadata_json_uri)

        if ns_name == '-':
            raise BauplanError(
                'Namespace must be specified. This restriction will be lifted in future versions.'
            )

        # Construct the path to the iceberg register endpoint
        # Path format: iceberg/v1/{branch}/namespaces/{namespace}/register
        path_parts = ['iceberg', 'v1', branch_name, 'namespaces', ns_name, 'register']

        # Make the API call to register the table using the iceberg proxy endpoint
        # This returns raw Iceberg REST API response, not wrapped in Bauplan metadata
        self._make_catalog_iceberg_call(
            method=Constants.HTTP_METHOD_POST,
            path=path_parts,
            body={
                'name': table_name,
                'metadata-location': metadata_json_uri,
                'overwrite': overwrite,
            },
        )

        # After registering, fetch the table metadata using get_table
        # This returns a properly formatted TableWithMetadata object
        return self.get_table(
            table=table_name,
            ref=branch_name,
            namespace=ns_name,
        )

    def revert_table(
        self,
        table: Union[str, Table],
        *,  # From here only keyword arguments are allowed
        namespace: Optional[Union[str, Namespace]] = None,
        source_ref: Union[str, Branch, Tag, Ref],
        into_branch: Union[str, Branch],
        replace: Optional[bool] = None,
        commit_body: Optional[str] = None,
        commit_properties: Optional[Dict[str, str]] = None,
    ) -> Branch:
        """
        Revert a table to a previous state.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.revert_table(
            table='my_table_name',
            namespace='my_namespace',
            source_ref='my_ref_or_branch_name',
            into_branch='main',
        )
        ```

        Parameters:
            table: The table to revert.
            namespace: The namespace of the table to revert.
            source_ref: The name of the source ref; either a branch like "main" or ref like "main@[sha]".
            into_branch: The name of the target branch where the table will be reverted.
            replace: Optional, whether to replace the table if it already exists.
            commit_body: Optional, the commit body message to attach to the operation.
            commit_properties: Optional, a list of properties to attach to the operation.
        Returns:
            The `bauplan.schema.Branch` where the revert was made.

        Raises:
            RevertTableForbiddenError: if the user does not have access to revert the table.
            RefNotFoundError: if the ref does not exist.
            BranchNotFoundError: if the destination branch does not exist.
            NotAWriteBranchError: if the destination branch is not a writable ref.
            BranchHeadChangedError: if the branch head hash has changed.
            MergeConflictError: if the merge operation results in a conflict.
            NamespaceConflictsError: if conflicting namespaces names are specified.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        table_name = _Validate.table_name('table', table)
        namespace_name = _Validate.optional_namespace_name('namespace', namespace)
        into_branch_name = _Validate.branch_name('into_branch', into_branch)
        source_ref_value = _Validate.ref('source_ref', source_ref)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_POST,
            path=[
                'v0',
                'refs',
                source_ref_value,
                'tables',
                table_name,
                'revert',
                into_branch_name,
            ],
            params={
                'namespace': namespace_name,
            },
            body={
                'replace': _Validate.optional_boolean('replace', replace),
                'commit_body': _Validate.optional_string('commit_body', commit_body),
                'commit_properties': _Validate.optional_properties('commit_properties', commit_properties),
            },
        )
        assert out.ref is not None
        return Branch(**out.ref.model_dump())

    def get_tags(
        self,
        *,  # From here only keyword arguments are allowed
        filter_by_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetTagsResponse:
        """
        Get all the tags.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        Parameters:
            filter_by_name: Optional, filter the commits by message.
            limit: Optional, max number of commits to get.
        Returns:
            A `bauplan.schema.GetTagsResponse` object.

        Raises:
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """

        params = {
            'filter_by_name': _Validate.optional_string('filter_by_name', filter_by_name),
        }
        limit = _Validate.optional_positive_int('limit', limit)

        return GetTagsResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                method=Constants.HTTP_METHOD_GET,
                path=['v0', 'tags'],
                params=params,
            ),
            data_mapper=Tag.model_validate,
            limit=limit,
            itersize=self.profile.itersize,
        )

    def get_tag(
        self,
        tag: Union[str, Tag],
    ) -> Tag:
        """
        Get the tag.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_tag
        import bauplan
        client = bauplan.Client()

        # retrieve only the tables as tuples of (name, kind)
        tag = client.get_tag('my_tag_name')
        ```

        Parameters:
            tag: The name of the tag to retrieve.
        Returns:
            A `bauplan.schema.Tag` object.

        Raises:
            TagNotFoundError: if the tag does not exist.
            NotATagRefError: if the object is not a tag.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        # Tag (with hash) is not supported in the catalog API
        tag_name = _Validate.tag_name('tag', tag)
        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_GET,
            path=['v0', 'tags', tag_name],
        )
        return Tag.model_validate(out.data)

    def has_tag(
        self,
        tag: Union[str, Tag],
    ) -> bool:
        """
        Check if a tag exists.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_tag
        import bauplan
        client = bauplan.Client()

        assert client.has_tag(
            tag='my_tag_name',
        )
        ```

        Parameters:
            tag: The tag to retrieve.
        Returns:
            A boolean for if the tag exists.

        Raises:
            NotATagRefError: if the object is not a tag.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        try:
            self.get_tag(tag=tag)
            return True
        except exceptions.TagNotFoundError:
            return False

    def create_tag(
        self,
        tag: Union[str, Tag],
        from_ref: Union[str, Branch, Ref],
        *,  # From here only keyword arguments are allowed
        if_not_exists: bool = False,
    ) -> Tag:
        """
        Create a new tag at a given ref.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.create_tag(
            tag='my_tag',
            from_ref='my_ref_or_branch_name',
        )
        ```

        Parameters:
            tag: The name of the new tag.
            from_ref: The name of the base branch; either a branch like "main" or ref like "main@[sha]".
            if_not_exists: If set to `True`, the tag will not be created if it already exists.
        Returns:
            The created `bauplan.schema.Tag` object.

        Raises:
            CreateTagForbiddenError: if the user does not have access to create the tag.
            RefNotFoundError: if the ref does not exist.
            TagExistsError: if the tag already exists.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        tag_name = _Validate.tag_name('tag', tag)
        from_ref_value = _Validate.ref('from_ref', from_ref)
        if_not_exists = _Validate.boolean('if_not_exists', if_not_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.TagExistsError,
            condition=if_not_exists,
            handler=lambda e: e.context_ref,
        ) as h:
            out = self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_POST,
                path=['v0', 'tags'],
                body={
                    'tag_name': tag_name,
                    'from_ref': from_ref_value,
                },
            )
            return Tag.model_validate(out.data)

        return h.value

    def rename_tag(
        self,
        tag: Union[str, Tag],
        new_tag: Union[str, Tag],
    ) -> Tag:
        """
        Rename an existing tag.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python notest
        import bauplan
        client = bauplan.Client()

        assert client.rename_tag(
            tag='old_tag_name',
            new_tag='new_tag_name',
        )
        ```

        Parameters:
            tag: The name of the tag to rename.
            new_tag: The name of the new tag.
        Returns:
            The renamed tag object.

        Raises:
            RenameTagForbiddenError: if the user does not have access to create the tag.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        tag_name = _Validate.tag_name('tag', tag)
        new_tag_name = _Validate.tag_name('new_tag', new_tag)

        out = self._make_catalog_api_call(
            method=Constants.HTTP_METHOD_PATCH,
            path=['v0', 'tags', tag_name],
            body={'tag_name': new_tag_name},
        )
        return Tag.model_validate(out.data)

    def delete_tag(
        self,
        tag: Union[str, Tag],
        *,  # From here only keyword arguments are allowed
        if_exists: bool = False,
    ) -> bool:
        """
        Delete a tag.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        ```python fixture:my_tag
        import bauplan
        client = bauplan.Client()

        assert client.delete_tag('my_tag_name')
        ```

        Parameters:
            tag: The name of the tag to delete.
            if_exists: If set to `True`, the tag will not raise an error if it does not exist.
        Returns:
            A boolean for if the tag was deleted.

        Raises:
            DeleteTagForbiddenError: if the user does not have access to delete the tag.
            TagNotFoundError: if the tag does not exist.
            NotATagRefError: if the object is not a tag.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        tag_value = _Validate.tag('tag', tag)
        if_exists = _Validate.boolean('if_exists', if_exists, False)

        with exceptions._soft_fail_if(
            exception_type=exceptions.TagNotFoundError,
            condition=if_exists,
            handler=lambda e: False,
        ) as h:
            self._make_catalog_api_call(
                method=Constants.HTTP_METHOD_DELETE,
                path=['v0', 'tags', str(tag_value)],
            )
            return True

        return h.value

    def _get_tag_by_job_id(self, job_id: str) -> Tag:
        """
        EXPERIMENTAL: Get a tag by job ID.

        Raises:
            TagNotFoundError: if the tag does not exist.
            NotATagRefError: if the object is not a tag.
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        job_id = _Validate.string('job_id', job_id)
        return self.get_tag(f'bpln.job_id.{job_id}')

    def _get_commit_by_job_id(self, job_id: str) -> Commit:
        """
        EXPERIMENTAL: Get a commit by job ID.

        Raises:
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        job_id = _Validate.string('job_id', job_id)
        commit = self.get_commits(f'bpln.job_id.{job_id}', limit=1)
        assert len(commit) == 1
        return commit[0]

    def get_commits(
        self,
        ref: Union[str, Branch, Tag, Ref],
        *,  # From here only keyword arguments are allowed
        filter_by_message: Optional[str] = None,
        filter_by_author_username: Optional[str] = None,
        filter_by_author_name: Optional[str] = None,
        filter_by_author_email: Optional[str] = None,
        filter_by_authored_date: Optional[Union[str, datetime]] = None,
        filter_by_authored_date_start_at: Optional[Union[str, datetime]] = None,
        filter_by_authored_date_end_at: Optional[Union[str, datetime]] = None,
        filter_by_parent_hash: Optional[str] = None,
        filter_by_properties: Optional[Dict[str, str]] = None,
        filter: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> GetCommitsResponse:
        """
        Get the commits for the target branch or ref.

        Upon failure, raises `bauplan.exceptions.BauplanError`

        Parameters:
            ref: The ref or branch to get the commits from.
            filter_by_message: Optional, filter the commits by message (can be a string or a regex like '^abc.*$')
            filter_by_author_username: Optional, filter the commits by author username (can be a string or a regex like '^abc.*$')
            filter_by_author_name: Optional, filter the commits by author name (can be a string or a regex like '^abc.*$')
            filter_by_author_email: Optional, filter the commits by author email (can be a string or a regex like '^abc.*$')
            filter_by_authored_date: Optional, filter the commits by the exact authored date.
            filter_by_authored_date_start_at: Optional, filter the commits by authored date start at.
            filter_by_authored_date_end_at: Optional, filter the commits by authored date end at.
            filter_by_parent_hash: Optional, filter the commits by parent hash.
            filter_by_properties: Optional, filter the commits by commit properties.
            filter: Optional, a CEL filter expression to filter the commits.
            limit: Optional, max number of commits to get.
        Returns:
            A `bauplan.schema.GetCommitsResponse` object.

        Raises:
            UnauthorizedError: if the user's credentials are invalid.
            ValueError: if one or more parameters are invalid.

        """
        ref_value = _Validate.ref('ref', ref)

        params = {
            'filter_by_message': _Validate.optional_string('filter_by_message', filter_by_message),
            'filter_by_author_username': _Validate.optional_string(
                'filter_by_author_username', filter_by_author_username
            ),
            'filter_by_author_name': _Validate.optional_string(
                'filter_by_author_name', filter_by_author_name
            ),
            'filter_by_author_email': _Validate.optional_string(
                'filter_by_author_email', filter_by_author_email
            ),
            'filter_by_authored_date': _Validate.optional_timestamp(
                'filter_by_authored_date', filter_by_authored_date
            ),
            'filter_by_authored_date_start_at': _Validate.optional_timestamp(
                'filter_by_authored_date_start_at', filter_by_authored_date_start_at
            ),
            'filter_by_authored_date_end_at': _Validate.optional_timestamp(
                'filter_by_authored_date_end_at', filter_by_authored_date_end_at
            ),
            'filter_by_parent_hash': _Validate.optional_string(
                'filter_by_parent_hash', filter_by_parent_hash
            ),
            'filter_by_properties': json.dumps(
                _Validate.optional_properties('filter_by_properties', filter_by_properties)
            ),
            'filter': _Validate.optional_string('filter', filter),
        }
        limit = _Validate.optional_positive_int('limit', limit)

        # TODO:
        # Recover these filters:
        # filter_by_committer_name: Optional[str] = None,
        # filter_by_committer_email: Optional[str] = None,
        # filter_by_committed_date: Optional[Union[str, datetime]] = None,
        # filter_by_committed_date_start_at: Optional[Union[str, datetime]] = None,
        # filter_by_committed_date_end_at: Optional[Union[str, datetime]] = None,
        # &&
        # 'filter_by_committer_name': _Validate.optional_string(
        #     'filter_by_committer_name', filter_by_committer_name
        # ),
        # 'filter_by_committer_email': _Validate.optional_string(
        #     'filter_by_committer_email', filter_by_committer_email
        # ),
        # 'filter_by_committed_date': _Validate.optional_timestamp(
        #     'filter_by_committed_date', filter_by_committed_date
        # ),
        # 'filter_by_committed_date_start_at': _Validate.optional_timestamp(
        #     'filter_by_committed_date_start_at', filter_by_committed_date_start_at
        # ),
        # 'filter_by_committed_date_end_at': _Validate.optional_timestamp(
        #     'filter_by_committed_date_end_at', filter_by_committed_date_end_at
        # ),

        return GetCommitsResponse(
            data_fetcher=self._new_paginate_api_data_fetcher(
                method=Constants.HTTP_METHOD_GET,
                path=['v0', 'refs', ref_value, 'commits'],
                params=params,
            ),
            data_mapper=Commit.model_validate,
            limit=limit,
            itersize=self.profile.itersize,
        )

    def info(
        self,
        debug: Optional[bool] = None,
        verbose: Optional[bool] = None,
        client_timeout: Optional[Union[int, float]] = None,
        **kwargs: Any,
    ) -> InfoState:
        """
        Fetch organization & account information.
        """
        return self._info.info(
            debug=debug,
            verbose=verbose,
            client_timeout=client_timeout,
            **kwargs,
        )

    # Helpers

    @_lifecycle
    def _make_catalog_api_call(
        self,
        method: str,
        path: Union[str, List[str], Tuple[str]],
        params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        pagination_token: Optional[str] = None,
        # shared
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> APIResponseWithData:
        """
        Helper to make a request to the API.
        """
        if isinstance(path, list) or isinstance(path, tuple):
            path = _Validate.quoted_url(*path)
        url = self.profile.catalog_endpoint + path
        headers = {Constants.HTTP_HEADER_PYPI_VERSION_KEY: BAUPLAN_VERSION}

        if self.profile.api_key:
            headers['Authorization'] = f'Bearer {self.profile.api_key}'

        if self.profile.feature_flags:
            headers[Constants.HTTP_HEADER_FEATURE_FLAGS] = json.dumps(self.profile.feature_flags)

        # Add client configuration defaults as headers
        params = params or {}
        if pagination_token and pagination_token.strip():
            params['pagination_token'] = pagination_token.strip()
        if 'default_namespace' not in params and self.profile.namespace:
            params['default_namespace'] = self.profile.namespace
        if 'cache' not in params and self.profile.cache is not None:
            params['cache'] = self.profile.cache
        if 'debug' not in params and self.profile.debug is not None:
            params['debug'] = 'true' if self.profile.debug else 'false'

        if body is not None and not isinstance(body, dict):
            raise exceptions.BauplanError(
                f'SDK INTERNAL ERROR: API request body must be dict, not {type(body)}'
            )
        res = requests.request(
            method,
            url,
            headers=headers,
            timeout=Constants.DEFAULT_API_CALL_TIMEOUT_SECONDS,
            params=params or {},
            json=body,
        )

        try:
            res_data = res.json()
            if res.status_code == 200:
                return APIResponseWithData.model_validate(res_data)

            if not isinstance(res_data, dict) or not res_data.get('metadata'):
                # We can't parse the response, raise a generic error
                raise exceptions.BauplanError(f'API response error: {res.status_code} - {res_data}')

            # This is a bauplan error
            if not res_data.get('error'):
                # This is the old response error, catalog is not updated yet
                res_data['error'] = {
                    'code': res.status_code,
                    'type': 'APIError',
                    'message': res_data.get('metadata', {})['error'],
                    'context': {},
                }
            raise exceptions.BauplanHTTPError.new_from_response(
                out=APIResponseWithError.model_validate(res_data),
            )
        except exceptions.BauplanHTTPError as e:
            raise e
        except pydantic.ValidationError as e:
            raise exceptions.BauplanError(f'API response parsing error: {e}') from e

    @_lifecycle
    def _make_catalog_iceberg_call(
        self,
        method: str,
        path: Union[str, List[str], Tuple[str]],
        params: Optional[Dict] = None,
        body: Optional[Dict] = None,
        # shared
        client_timeout: Optional[Union[int, float]] = None,
        lifecycle_handler: Optional[_JobLifeCycleHandler] = None,
    ) -> Dict:
        """
        Helper to make a request to the Iceberg proxy API endpoints.

        These endpoints return raw Iceberg REST API responses as dictionaries.
        """
        if isinstance(path, list) or isinstance(path, tuple):
            path = _Validate.quoted_url(*path)

        url = self.profile.api_endpoint + path
        headers = {Constants.HTTP_HEADER_PYPI_VERSION_KEY: BAUPLAN_VERSION}

        if self.profile.api_key:
            headers['Authorization'] = f'Bearer {self.profile.api_key}'

        # Add client configuration defaults as params
        if body is not None and not isinstance(body, dict):
            raise exceptions.BauplanError(
                f'SDK INTERNAL ERROR: API request body must be dict, not {type(body)}'
            )

        res = requests.request(
            method,
            url,
            headers=headers,
            timeout=Constants.DEFAULT_API_CALL_TIMEOUT_SECONDS,
            params=params or {},
            json=body,
        )

        try:
            res_data = res.json()
            if res.status_code == 200:
                return res_data

            # For non-200 responses, try to parse as Bauplan error format
            if not isinstance(res_data, dict) or not res_data.get('metadata'):
                # We can't parse the response, raise a generic error
                raise exceptions.BauplanError(f'API response error: {res.status_code} - {res_data}')

            # This is a bauplan error
            if not res_data.get('error'):
                # This is the old response error format, catalog is not updated yet
                res_data['error'] = {
                    'code': res.status_code,
                    'type': 'APIError',
                    'message': res_data.get('metadata', {}).get('error', 'Unknown error'),
                    'context': {},
                }
            raise exceptions.BauplanHTTPError.new_from_response(
                out=APIResponseWithError.model_validate(res_data),
            )
        except exceptions.BauplanHTTPError as e:
            raise e
        except pydantic.ValidationError as e:
            raise exceptions.BauplanError(f'API response parsing error: {e}') from e
        except requests.exceptions.JSONDecodeError as e:
            raise exceptions.BauplanError(f'Failed to parse JSON response: {res.text}') from e

    def _new_paginate_api_data_fetcher(
        self, method: str, path: Union[str, List[str]], params: dict[str, Any]
    ) -> Callable[[int, Optional[str]], APIResponse]:
        """
        Helper to create a new data fetcher.
        """

        def _fetcher(max_records: int, pagination_token: Optional[str]) -> APIResponse:
            return self._make_catalog_api_call(
                method=method,
                path=path,
                params={**params, 'max_records': max_records},
                pagination_token=pagination_token,
            )

        return _fetcher
