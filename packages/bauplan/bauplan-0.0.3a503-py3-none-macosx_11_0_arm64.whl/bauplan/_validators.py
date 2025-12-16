from __future__ import annotations

import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from google.protobuf.timestamp_pb2 import Timestamp

from ._bpln_proto.commander.service.v2 import common_pb2 as common_pb
from ._bpln_proto.commander.service.v2.common_pb2 import JobRequestOptionalBool
from .schema import Branch, JobKind, JobState, Namespace, Ref, Table, Tag


class _Validate:
    @classmethod
    def quoted_url(cls, *args) -> str:
        """
        Helper to build a URL from parts, safely handling slashes.
        """
        return '/' + '/'.join([urllib.parse.quote(x, safe='') for x in args])

    @classmethod
    def parameters(
        cls,
        name: str,
        parameters: Optional[Dict[str, Optional[Union[str, int, float, bool]]]] = None,
    ) -> Dict[str, Optional[Union[str, int, float, bool]]]:
        """
        Default branch is the local active branch, but can be overridden by passing a ref.
        It's optional because the default ref is managed by the service.
        """
        if parameters is None:
            return {}
        if not isinstance(parameters, dict):
            raise ValueError(f'{name} must be a dict or None')
        return parameters

    @classmethod
    def feature_flags(cls, name: str, flags: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        flags = cls.parameters(name, flags)
        ff_normalized: Dict[str, str] = {}
        for key, value in flags.items():
            if isinstance(value, bool):
                ff_normalized[key] = 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                ff_normalized[key] = str(value)
            elif not isinstance(key, str):
                raise ValueError(f'{name} keys must be str | int | float')
            elif not isinstance(value, str):
                raise ValueError(f'{name} values must be str | int | float')
            else:
                ff_normalized[key] = value
        return ff_normalized

    @classmethod
    def string(cls, name: str, value: Optional[str] = None, default: Optional[str] = None) -> str:
        try:
            value = cls.optional_string(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string') from e
        return value

    @classmethod
    def optional_string(cls, name: str, value: Optional[str], default: Optional[str] = None) -> Optional[str]:
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, str) and value.strip() != '':
            return value
        raise ValueError(f'{name} can be None or a non-empty string')

    @classmethod
    def optional_int(cls, name: str, value: Optional[int], default: Optional[int] = None) -> Optional[int]:
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, int):
            return value
        raise ValueError(f'{name} can be None or an int')

    @classmethod
    def optional_positive_int(
        cls, name: str, value: Optional[int], default: Optional[int] = None
    ) -> Optional[int]:
        try:
            value = cls.optional_int(name, value, default)
            if value is not None and value < 1:
                raise ValueError
        except Exception as e:
            raise ValueError(f'{name} can be None or a positive int') from e
        return value

    @classmethod
    def optional_datetime(
        cls,
        name: str,
        value: Optional[Union[str, datetime]],
        default: Optional[Union[str, datetime]] = None,
    ) -> Optional[datetime]:
        value = default if value is None else value
        if value is None:
            return None

        if isinstance(value, str):
            if not value.strip():
                raise ValueError(f'{name} must be a non-empty ISO format string, datetime, or None')
            # Normalize 'Z' suffix to '+00:00' for Python 3.10 compatibility
            normalized = value.strip()
            if normalized.endswith('Z'):
                normalized = normalized[:-1] + '+00:00'
            try:
                value = datetime.fromisoformat(normalized)
            except ValueError as e:
                raise ValueError(
                    f'{name} must be a valid ISO format string (e.g., "2024-01-15T10:30:00Z"), got: {value!r}'
                ) from e

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)

        raise ValueError(f'{name} must be a str, datetime, or None')

    @classmethod
    def optional_timestamp(
        cls,
        name: str,
        value: Optional[Union[str, datetime]],
        default: Optional[Union[str, datetime]] = None,
    ) -> Optional[str]:
        dt = cls.optional_datetime(name, value, default)
        if dt is None:
            return None
        return dt.isoformat()

    @classmethod
    def optional_pb_timestamp(
        cls,
        name: str,
        value: Optional[Union[str, datetime]],
        default: Optional[Union[str, datetime]] = None,
    ) -> Optional[Timestamp]:
        dt = cls.optional_datetime(name, value, default)
        if dt is None:
            return None
        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts

    @classmethod
    def ref(
        cls,
        name: str,
        value: Optional[Union[str, Branch, Tag, Ref]],
        default: Optional[Union[str, Branch, Tag, Ref]] = None,
    ) -> str:
        """
        Get the ref from a string or ref-like object.
        """
        try:
            value = cls.optional_ref(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Branch or Tag object') from e
        return value

    @classmethod
    def optional_ref(
        cls,
        name: str,
        value: Optional[Union[str, Branch, Tag, Ref]],
        default: Optional[Union[str, Branch, Tag, Ref]] = None,
    ) -> Optional[str]:
        """
        Get the ref from a string or ref-like object.

        """
        value = default if value is None else value
        if value is None:
            return value
        if isinstance(value, str) and value.strip() != '':
            return value
        if isinstance(value, (Branch, Tag, Ref)) and value.name.strip() != '':
            return str(value)
        raise ValueError(f'{name} can be None, a non-empty string or a valid Branch or Tag object')

    @classmethod
    def boolean(cls, name: str, value: Optional[bool], default: Optional[bool] = None) -> bool:
        try:
            value = cls.optional_boolean(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a bool') from e
        return value

    @classmethod
    def optional_boolean(
        cls, name: str, value: Optional[bool] = None, default: Optional[bool] = None
    ) -> Optional[bool]:
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        raise ValueError(f'{name} can be None or a bool')

    @classmethod
    def pb2_optional_boolean(
        cls, name: str, value: Optional[bool], default: Optional[bool] = None
    ) -> Tuple[Optional[bool], JobRequestOptionalBool]:
        value = cls.optional_boolean(name, value, default)
        if value is True:
            return value, JobRequestOptionalBool.JOB_REQUEST_OPTIONAL_BOOL_TRUE
        if value is False:
            return value, JobRequestOptionalBool.JOB_REQUEST_OPTIONAL_BOOL_FALSE
        return value, JobRequestOptionalBool.JOB_REQUEST_OPTIONAL_BOOL_UNSPECIFIED

    @classmethod
    def optional_on_off_flag(
        cls,
        name: str,
        value: Optional[Union[bool, str]],
        default: Optional[Union[bool, str]] = None,
    ) -> Optional[str]:
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, str) and value.strip() != '':
            return value.strip()
        raise ValueError(f'{name} must be a bool or a non-empty string or None')

    @classmethod
    def namespace(
        cls,
        name: str,
        value: Optional[Union[str, Namespace]],
        default: Optional[Union[str, Namespace]] = None,
    ) -> Namespace:
        """
        Default namespace is read from the local config, but can be overridden by the user.
        It's optional because the default namespace is managed by the service.
        """
        try:
            namespace = cls.optional_namespace(name, value, default)
            assert namespace is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Namespace object') from e
        return namespace

    @classmethod
    def optional_namespace(
        cls,
        name: str,
        value: Optional[Union[str, Namespace]],
        default: Optional[Union[str, Namespace]] = None,
    ) -> Optional[Namespace]:
        """
        Default namespace is read from the local config, but can be overridden by the user.
        It's optional because the default namespace is managed by the service.
        """
        value = default if value is None else value
        if value is None:
            return None
        try:
            if isinstance(value, str):
                assert value.strip() != ''
                value = Namespace(name=value)
            assert isinstance(value, Namespace)
        except Exception as e:
            raise ValueError(f'{name} can be None, a non-empty string or a valid Namespace object') from e
        return value

    @classmethod
    def namespace_name(
        cls,
        name: str,
        value: Optional[Union[str, Namespace]],
        default: Optional[Union[str, Namespace]] = None,
    ) -> str:
        """
        Get the namespace name from a namespace or namespace-like object.
        """
        return cls.namespace(name, value, default).name

    @classmethod
    def optional_namespace_name(
        cls,
        name: str,
        value: Optional[Union[str, Namespace]],
        default: Optional[Union[str, Namespace]] = None,
    ) -> Optional[str]:
        """
        Get the namespace name from a namespace or namespace-like object.
        """
        value = cls.optional_namespace(name, value, default)
        return None if value is None else value.name

    @classmethod
    def optional_properties(cls, name: str, properties: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Validate and return the properties dict.
        """
        out_properties: Dict[str, str] = {}
        if properties is not None:
            if not isinstance(properties, dict):
                raise ValueError(f'{name} must be a dict or None')
            for key, value in properties.items():
                if not isinstance(key, str):
                    raise ValueError(f'{name} keys must be str, got {key} as {type(key)}')
                if key.strip() == '':
                    raise ValueError(f'{name} keys must be non-empty strings')
                if not isinstance(value, str):
                    raise ValueError(f'{name} values must be str, got {value} as {type(value)}')
                if value.strip() == '':
                    raise ValueError(f'{name} values must be non-empty strings')
                out_properties[key.strip()] = value.strip()
        return out_properties

    @classmethod
    def table_name(cls, name: str, value: Optional[Union[str, Table]]) -> str:
        """
        Get the table name from a table or table-like object.
        """
        try:
            value = cls.optional_table_name(name, value)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Table object') from e
        return value

    @classmethod
    def optional_table_name(cls, name: str, value: Optional[Union[str, Table]]) -> Optional[str]:
        """
        Get the table name from a table or table-like object.
        """
        if value is None:
            return None
        if isinstance(value, str) and value.strip() != '':
            return value
        if isinstance(value, Table) and value.name.strip() != '':
            return value.fqn
        raise ValueError(f'{name} can be None, a non-empty string or a valid Table object')

    @classmethod
    def branch(
        cls, name: str, value: Optional[Union[str, Branch]], default: Optional[Union[str, Branch]] = None
    ) -> Branch:
        """
        Get the branch from a string or branch-like object.
        """
        try:
            value = cls.optional_branch(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Branch object') from e
        return value

    @classmethod
    def optional_branch(
        cls, name: str, value: Optional[Union[str, Branch]], default: Optional[Union[str, Branch]] = None
    ) -> Optional[Branch]:
        """
        Get the branch from a string or branch-like object.
        """
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, str) and value.strip() != '':
            value = Branch.from_string(value)
        if isinstance(value, Branch) and value.name.strip() != '':
            return value
        raise ValueError(f'{name} can be None, a non-empty string or a valid Branch object')

    @classmethod
    def branch_name(
        cls, name: str, value: Optional[Union[str, Branch]], default: Optional[Union[str, Branch]] = None
    ) -> str:
        """
        Get the branch name from a branch or branch-like object.
        """
        return cls.branch(name, value, default).name

    @classmethod
    def optional_branch_name(
        cls, name: str, value: Optional[Union[str, Branch]], default: Optional[Union[str, Branch]] = None
    ) -> Optional[str]:
        """
        Get the branch name from a branch or branch-like object.
        """
        try:
            value = cls.optional_branch(name, value, default)
            if value is None:
                return None
        except Exception as e:
            raise ValueError(f'{name} can be None, a non-empty string or a valid Branch object') from e
        return value.name

    @classmethod
    def tag(
        cls, name: str, value: Optional[Union[str, Tag]], default: Optional[Union[str, Tag]] = None
    ) -> Tag:
        """
        Get the tag from a string or tag-like object.
        """
        try:
            value = cls.optional_tag(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Tag object') from e
        return value

    @classmethod
    def optional_tag(
        cls, name: str, value: Optional[Union[str, Tag]], default: Optional[Union[str, Tag]] = None
    ) -> Optional[Tag]:
        """
        Get the tag from a string or tag-like object.
        """
        value = default if value is None else value
        if value is None:
            return None
        if isinstance(value, str) and value.strip() != '':
            return Tag.from_string(value)
        if isinstance(value, Tag) and value.name.strip() != '':
            return value
        raise ValueError(f'{name} can be None, a non-empty string or a valid Tag object')

    @classmethod
    def tag_name(
        cls, name: str, value: Optional[Union[str, Tag]], default: Optional[Union[str, Tag]] = None
    ) -> str:
        """
        Get the tag name from a tag or tag-like object.
        """
        try:
            value = cls.optional_tag(name, value, default)
            assert value is not None
        except Exception as e:
            raise ValueError(f'{name} must be a non-empty string or a valid Tag object') from e
        return value.name

    @classmethod
    def optional_tag_name(
        cls, name: str, value: Optional[Union[str, Tag]], default: Optional[Union[str, Tag]] = None
    ) -> Optional[str]:
        """
        Get the tag name from a tag or tag-like object.
        """
        try:
            value = cls.optional_tag(name, value, default)
        except Exception as e:
            raise ValueError(f'{name} can be None, a non-empty string or a valid Tag object') from e
        return None if value is None else value.name

    @classmethod
    def args(
        cls, name: str, args: Optional[Dict[str, str]], default: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Validate and return the args dict.
        """
        if args is not None:
            if not isinstance(args, dict):
                raise ValueError(f'{name} must be a dict or None')
        return {
            **(default or {}),
            **(args or {}),
        }

    @classmethod
    def ensure_parent_dir_exists(cls, name: str, path: Union[str, Path]) -> Path:
        abs_path = Path(path).expanduser().resolve()
        parent_dir = abs_path.parent
        if not parent_dir.exists():
            raise FileNotFoundError(f'{name} is an invalid path, directory {parent_dir} does not exist')
        return abs_path

    @classmethod
    def _get_log_ts_str(cls, val: int) -> str:
        """
        Output ISO timestamp to the decisecond from a nanosecond integer timestamp input.
        """
        return str(datetime.fromtimestamp(round(val / 1000000000, 2)))[:21]

    @classmethod
    def optional_endpoint(cls, name: str, endpoint: Optional[str]) -> Optional[str]:
        if endpoint is None:
            return None
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise ValueError(f'{name} must be a valid string or None')
        endpoint = endpoint.strip()
        proto_match = re.match(r'^([^:]+)://(.*)$', endpoint.lower())
        if not proto_match:
            endpoint = f'https://{endpoint}'
        else:
            if proto_match.group(1) not in ('http', 'https'):
                raise ValueError(f'{name} must be a valid URL: invalid protocol')
            if not proto_match.group(2):
                ValueError(f'{name} must be a valid URL: missing hostname')
        # removing all trailing slashes
        return re.sub(r'/*$', '', endpoint)

    @classmethod
    def string_list(cls, name: str, value: List[str]) -> List[str]:
        """
        Validate and return a list of non-empty strings.
        """
        if isinstance(value, str):
            return [value] if value.strip() != '' else []
        if not isinstance(value, (list, tuple, set)):
            raise ValueError(f'{name} must be a list of strings')
        for idx, item in enumerate(value):
            if not isinstance(item, str):
                raise ValueError(f'{name}[{idx}] must be a string, got {type(item)}')
            if item.strip() == '':
                raise ValueError(f'{name}[{idx}] must be a non-empty string')
        return value

    @classmethod
    def optional_string_list(cls, name: str, value: Optional[List[str]]) -> List[str]:
        """
        Validate and return a list of non-empty strings.
        """
        if value is None:
            return []
        return cls.string_list(name, value)

    @classmethod
    def optional_pb_job_status_types(
        cls,
        name: str,
        value: Optional[Union[str, JobState, List[Union[str, JobState]]]],
    ) -> List[common_pb.JobStateType]:
        """
        Validate and return a list of job statuses.
        """
        if value is None:
            return []

        statuses: Set[common_pb.JobStateType] = set()
        if isinstance(value, (list, tuple, set)):
            for item in value:
                statuses.update(cls.optional_pb_job_status_types(name, item))
        else:
            if isinstance(value, JobState):
                statuses.add(value.value)
            elif isinstance(value, str):
                statuses.add(JobState.from_string(value).value)
            else:
                raise ValueError(f'{name} must be str, JobState, or list of str/JobState')
        return list(statuses)

    @classmethod
    def optional_pb_job_kinds(
        cls,
        name: str,
        value: Optional[Union[str, JobKind, List[Union[str, JobKind]]]],
    ) -> List[common_pb.JobKind]:
        """
        Validate and return a list of job kinds.
        """
        if value is None:
            return []

        statuses: Set[common_pb.JobKind] = set()
        if isinstance(value, (list, tuple, set)):
            for item in value:
                statuses.update(cls.optional_pb_job_kinds(name, item))
        else:
            if isinstance(value, JobKind):
                statuses.add(value.value)
            elif isinstance(value, str):
                statuses.add(JobKind.from_string(value).value)
            else:
                raise ValueError(f'{name} must be str, JobKind, or list of str/JobKind')
        return list(statuses)
