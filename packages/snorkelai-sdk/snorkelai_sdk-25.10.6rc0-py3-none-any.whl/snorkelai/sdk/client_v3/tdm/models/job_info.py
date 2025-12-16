import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs
from dateutil.parser import isoparse

from ..models.job_state import JobState
from ..models.job_type import JobType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.job_group import JobGroup  # noqa: F401
    from ..models.job_info_detail import JobInfoDetail  # noqa: F401
    from ..models.job_info_timing import JobInfoTiming  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="JobInfo")


@attrs.define
class JobInfo:
    """Class used to track asynchronous jobs.

    Attributes:
        job_type (JobType):
        state (JobState):
        uid (str):
        application_name (Union[Unset, str]):
        application_uid (Union[Unset, int]):
        created_by_username (Union[Unset, str]):
        dataset_uid (Union[Unset, int]):
        dependency_job_ids (Union[Unset, List[str]]):
        detail (Union[Unset, JobInfoDetail]):
        end_time (Union[Unset, datetime.datetime]): If null, job has not finished.
        enqueued_time (Union[Unset, datetime.datetime]): We don't expect enqueued time to be null, but if it is, job has
            not been fully queued up yet
        execution_start_time (Union[Unset, datetime.datetime]): If this field is null, job has not been picked up by a
            worker yet
        function_name (Union[Unset, str]):
        job_group (Union[Unset, JobGroup]):
        message (Union[Unset, str]):
        node_uid (Union[Unset, int]):
        percent (Union[Unset, int]):
        pod_name (Union[Unset, str]):
        process_id (Union[Unset, int]):
        sub_message (Union[Unset, str]):
        timing (Union[Unset, JobInfoTiming]):
        user_uid (Union[Unset, int]):
        workspace_uid (Union[Unset, int]):
    """

    job_type: JobType
    state: JobState
    uid: str
    application_name: Union[Unset, str] = UNSET
    application_uid: Union[Unset, int] = UNSET
    created_by_username: Union[Unset, str] = UNSET
    dataset_uid: Union[Unset, int] = UNSET
    dependency_job_ids: Union[Unset, List[str]] = UNSET
    detail: Union[Unset, "JobInfoDetail"] = UNSET
    end_time: Union[Unset, datetime.datetime] = UNSET
    enqueued_time: Union[Unset, datetime.datetime] = UNSET
    execution_start_time: Union[Unset, datetime.datetime] = UNSET
    function_name: Union[Unset, str] = UNSET
    job_group: Union[Unset, "JobGroup"] = UNSET
    message: Union[Unset, str] = UNSET
    node_uid: Union[Unset, int] = UNSET
    percent: Union[Unset, int] = UNSET
    pod_name: Union[Unset, str] = UNSET
    process_id: Union[Unset, int] = UNSET
    sub_message: Union[Unset, str] = UNSET
    timing: Union[Unset, "JobInfoTiming"] = UNSET
    user_uid: Union[Unset, int] = UNSET
    workspace_uid: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.job_group import JobGroup  # noqa: F401
        from ..models.job_info_detail import JobInfoDetail  # noqa: F401
        from ..models.job_info_timing import JobInfoTiming  # noqa: F401
        # fmt: on
        job_type = self.job_type.value
        state = self.state.value
        uid = self.uid
        application_name = self.application_name
        application_uid = self.application_uid
        created_by_username = self.created_by_username
        dataset_uid = self.dataset_uid
        dependency_job_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.dependency_job_ids, Unset):
            dependency_job_ids = self.dependency_job_ids

        detail: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.detail, Unset):
            detail = self.detail.to_dict()
        end_time: Union[Unset, str] = UNSET
        if not isinstance(self.end_time, Unset):
            end_time = self.end_time.isoformat()
        enqueued_time: Union[Unset, str] = UNSET
        if not isinstance(self.enqueued_time, Unset):
            enqueued_time = self.enqueued_time.isoformat()
        execution_start_time: Union[Unset, str] = UNSET
        if not isinstance(self.execution_start_time, Unset):
            execution_start_time = self.execution_start_time.isoformat()
        function_name = self.function_name
        job_group: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.job_group, Unset):
            job_group = self.job_group.to_dict()
        message = self.message
        node_uid = self.node_uid
        percent = self.percent
        pod_name = self.pod_name
        process_id = self.process_id
        sub_message = self.sub_message
        timing: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.timing, Unset):
            timing = self.timing.to_dict()
        user_uid = self.user_uid
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_type": job_type,
                "state": state,
                "uid": uid,
            }
        )
        if application_name is not UNSET:
            field_dict["application_name"] = application_name
        if application_uid is not UNSET:
            field_dict["application_uid"] = application_uid
        if created_by_username is not UNSET:
            field_dict["created_by_username"] = created_by_username
        if dataset_uid is not UNSET:
            field_dict["dataset_uid"] = dataset_uid
        if dependency_job_ids is not UNSET:
            field_dict["dependency_job_ids"] = dependency_job_ids
        if detail is not UNSET:
            field_dict["detail"] = detail
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if enqueued_time is not UNSET:
            field_dict["enqueued_time"] = enqueued_time
        if execution_start_time is not UNSET:
            field_dict["execution_start_time"] = execution_start_time
        if function_name is not UNSET:
            field_dict["function_name"] = function_name
        if job_group is not UNSET:
            field_dict["job_group"] = job_group
        if message is not UNSET:
            field_dict["message"] = message
        if node_uid is not UNSET:
            field_dict["node_uid"] = node_uid
        if percent is not UNSET:
            field_dict["percent"] = percent
        if pod_name is not UNSET:
            field_dict["pod_name"] = pod_name
        if process_id is not UNSET:
            field_dict["process_id"] = process_id
        if sub_message is not UNSET:
            field_dict["sub_message"] = sub_message
        if timing is not UNSET:
            field_dict["timing"] = timing
        if user_uid is not UNSET:
            field_dict["user_uid"] = user_uid
        if workspace_uid is not UNSET:
            field_dict["workspace_uid"] = workspace_uid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.job_group import JobGroup  # noqa: F401
        from ..models.job_info_detail import JobInfoDetail  # noqa: F401
        from ..models.job_info_timing import JobInfoTiming  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        job_type = JobType(d.pop("job_type"))

        state = JobState(d.pop("state"))

        uid = d.pop("uid")

        _application_name = d.pop("application_name", UNSET)
        application_name = UNSET if _application_name is None else _application_name

        _application_uid = d.pop("application_uid", UNSET)
        application_uid = UNSET if _application_uid is None else _application_uid

        _created_by_username = d.pop("created_by_username", UNSET)
        created_by_username = (
            UNSET if _created_by_username is None else _created_by_username
        )

        _dataset_uid = d.pop("dataset_uid", UNSET)
        dataset_uid = UNSET if _dataset_uid is None else _dataset_uid

        _dependency_job_ids = d.pop("dependency_job_ids", UNSET)
        dependency_job_ids = cast(
            List[str], UNSET if _dependency_job_ids is None else _dependency_job_ids
        )

        _detail = d.pop("detail", UNSET)
        _detail = UNSET if _detail is None else _detail
        detail: Union[Unset, JobInfoDetail]
        if isinstance(_detail, Unset):
            detail = UNSET
        else:
            detail = JobInfoDetail.from_dict(_detail)

        _end_time = d.pop("end_time", UNSET)
        _end_time = UNSET if _end_time is None else _end_time
        end_time: Union[Unset, datetime.datetime]
        if isinstance(_end_time, Unset):
            end_time = UNSET
        else:
            end_time = isoparse(_end_time)

        _enqueued_time = d.pop("enqueued_time", UNSET)
        _enqueued_time = UNSET if _enqueued_time is None else _enqueued_time
        enqueued_time: Union[Unset, datetime.datetime]
        if isinstance(_enqueued_time, Unset):
            enqueued_time = UNSET
        else:
            enqueued_time = isoparse(_enqueued_time)

        _execution_start_time = d.pop("execution_start_time", UNSET)
        _execution_start_time = (
            UNSET if _execution_start_time is None else _execution_start_time
        )
        execution_start_time: Union[Unset, datetime.datetime]
        if isinstance(_execution_start_time, Unset):
            execution_start_time = UNSET
        else:
            execution_start_time = isoparse(_execution_start_time)

        _function_name = d.pop("function_name", UNSET)
        function_name = UNSET if _function_name is None else _function_name

        _job_group = d.pop("job_group", UNSET)
        _job_group = UNSET if _job_group is None else _job_group
        job_group: Union[Unset, JobGroup]
        if isinstance(_job_group, Unset):
            job_group = UNSET
        else:
            job_group = JobGroup.from_dict(_job_group)

        _message = d.pop("message", UNSET)
        message = UNSET if _message is None else _message

        _node_uid = d.pop("node_uid", UNSET)
        node_uid = UNSET if _node_uid is None else _node_uid

        _percent = d.pop("percent", UNSET)
        percent = UNSET if _percent is None else _percent

        _pod_name = d.pop("pod_name", UNSET)
        pod_name = UNSET if _pod_name is None else _pod_name

        _process_id = d.pop("process_id", UNSET)
        process_id = UNSET if _process_id is None else _process_id

        _sub_message = d.pop("sub_message", UNSET)
        sub_message = UNSET if _sub_message is None else _sub_message

        _timing = d.pop("timing", UNSET)
        _timing = UNSET if _timing is None else _timing
        timing: Union[Unset, JobInfoTiming]
        if isinstance(_timing, Unset):
            timing = UNSET
        else:
            timing = JobInfoTiming.from_dict(_timing)

        _user_uid = d.pop("user_uid", UNSET)
        user_uid = UNSET if _user_uid is None else _user_uid

        _workspace_uid = d.pop("workspace_uid", UNSET)
        workspace_uid = UNSET if _workspace_uid is None else _workspace_uid

        obj = cls(
            job_type=job_type,
            state=state,
            uid=uid,
            application_name=application_name,
            application_uid=application_uid,
            created_by_username=created_by_username,
            dataset_uid=dataset_uid,
            dependency_job_ids=dependency_job_ids,
            detail=detail,
            end_time=end_time,
            enqueued_time=enqueued_time,
            execution_start_time=execution_start_time,
            function_name=function_name,
            job_group=job_group,
            message=message,
            node_uid=node_uid,
            percent=percent,
            pod_name=pod_name,
            process_id=process_id,
            sub_message=sub_message,
            timing=timing,
            user_uid=user_uid,
            workspace_uid=workspace_uid,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
