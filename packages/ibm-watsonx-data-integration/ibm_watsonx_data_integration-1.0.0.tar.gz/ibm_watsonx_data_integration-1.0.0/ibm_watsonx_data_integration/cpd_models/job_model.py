#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""Module containing Job and Job Run Models."""

import datetime
import json
import requests
import yaml
from enum import Enum
from ibm_watsonx_data_integration.common.exceptions import IbmCloudApiException
from ibm_watsonx_data_integration.common.json_patch_format import prepare_json_patch_payload
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.flow_model import DefaultFlowPayloadExtender, Flow, PayloadExtender
from ibm_watsonx_data_integration.services.datastage.models.flow import BatchFlow, BatchFlowPayloadExtender
from ibm_watsonx_data_integration.services.streamsets.models import StreamingFlow
from ibm_watsonx_data_integration.services.streamsets.models.flow_model import StreamingFlowPayloadExtender
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Optional
from typing_extensions import override

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform

RepeatMode = Literal["minutely", "hourly", "daily", "weekly", "monthly"]


_DAY_OF_WEEK_TO_INT = {
    "SUNDAY": 0,
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
}


class Outputs(BaseModel):
    """Holds job configuration output information."""

    total_rows_read: int = Field(repr=False, default=0)
    total_rows_written: int = Field(repr=False, default=0)
    total_bytes_read: int = Field(repr=False, default=0)
    total_bytes_written: int = Field(repr=False, default=0)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class JobConfiguration(BaseModel):
    """Holds configuration parameters which Job was run."""

    env_id: str = Field(repr=False, default="")
    env_type: str = Field(repr=False, default="")
    flow_limits: dict[str, int] = Field(default={"warn_limit": 0}, repr=False)
    env_variables: list[str] | None = Field(repr=False, default_factory=list)  # noqa
    version: str = Field(repr=False, default="")
    deployment_job_definition_id: str = Field(repr=False, default="")
    outputs: Outputs = Field(frozen=True, repr=False, default_factory=Outputs)
    offset: dict[str, Any] | None = Field(default=None, repr=False)

    _expose: bool = PrivateAttr(default=False)


class JobParameter(BaseModel):
    """Parameter used when running job.

    Represents parameter used by Connectors and Stages to dynamically
    change value.
    """

    name: str
    value: Any

    _expose: bool = PrivateAttr(default=False)


class ParameterSet(BaseModel):
    """Parameter sets."""

    name: str
    value_set: str | None = Field(default=None, frozen=False, repr=False)
    ref: str = Field(frozen=True, repr=False)

    _expose: bool = PrivateAttr(default=False)


class RetentionPolicy(BaseModel):
    """Retention policy model."""

    days: int | None = None
    amount: int | None = None

    _expose: bool = PrivateAttr(default=False)


class NotificationTypes(BaseModel):
    """Notification Types model."""

    success: bool = False
    warning: bool = False
    failure: bool = False

    _expose: bool = PrivateAttr(default=False)


class ScheduleInfo(BaseModel):
    """Represent schedule configuration for Job."""

    repeat: bool | None = None
    start_on: int | None = Field(alias="startOn", default=None)
    end_on: int | None = Field(alias="endOn", default=None)

    # TODO: change to `validate_by_name` when update pydantic version >=2.11
    model_config = ConfigDict(populate_by_name=True)
    _expose: bool = PrivateAttr(default=False)


class Schedule(BaseModel):
    """Provide details about scheduling a job.

    Args:
        start_date: The scheduled job will be triggered after this timestamp. Format: yyyy-mm-dd hh-mm
        repeat_mode: When to repeat the job. Options are minutely, hourly, daily, weekly, monthly.
        repeat_value: Values to accompany repeat_mode. These values have different types depending on the repeat_mode.
                      minutely: int. Repeats every repeat_value minutes
                      hourly: int. Repeats at repeat_value minutes past hour
                      daily: datetime.time. Repeats every day at repeat_value
                      weekly: tuple. First value represents the day of the week, second value is the time.
                      monthly: tuple. First value represents the day of the month, second value is the time.
        exclude_days: Days to exclude. Only available when repeat_mode is minutely, hourly, or daily.
                      0-6 corresponds to Sunday-Saturday.
        end_date: The date to end the schedule. Format: yyyy-mm-dd hh-mm
    """

    start_date: datetime.datetime = None
    repeat_mode: RepeatMode = None
    repeat_value: int | datetime.time | tuple[int | str, datetime.time] = None
    exclude_days: list[int] = None
    end_date: datetime.datetime = None


class JobRunState(str, Enum):
    """Available states for Job Run."""

    Queued = "Queued"
    Starting = "Starting"
    Running = "Running"
    Paused = "Paused"
    Resuming = "Resuming"
    Canceling = "Canceling"
    Canceled = "Canceled"
    Failed = "Failed"
    Completed = "Completed"
    CompletedWithErrors = "CompletedWithErrors"
    CompletedWithWarnings = "CompletedWithWarnings"


class JobRunMetadata(BaseModel):
    """Model representing metadata for a Job Run."""

    name: str = Field(repr=True)
    asset_id: str = Field(repr=False)
    owner_id: str = Field(repr=False)
    created: int = Field(repr=False)
    created_at: str = Field(repr=False)
    usage: dict[str, Any] = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class JobRun(BaseModel):
    """The model for CPD Job Run."""

    metadata: JobRunMetadata = Field(repr=True)

    job_id: str = Field(repr=False, alias="job_ref")
    job_name: str = Field(repr=True)
    job_type: str = Field(repr=False)
    job_run_id: str = Field(
        repr=True, default_factory=lambda fields: fields["metadata"].asset_id, frozen=True, exclude=True
    )
    state: JobRunState = Field(repr=True)
    is_scheduled_run: bool = Field(alias="isScheduledRun", repr=False, default=False)
    configuration: JobConfiguration = Field(repr=False)
    project_name: str | None = Field(repr=False, default=None)
    queue_start: int | None = Field(repr=False, default=None)
    last_state_change_timestamp: str | None = Field(repr=False, default=None)
    job_parameters: list[JobParameter] | None = Field(repr=False, default=None)
    queue_end: int | None = Field(repr=False, default=None)
    runtime_job_id: str | None = Field(repr=False, default=None)
    parameter_sets: list[ParameterSet] | None = Field(repr=False, default=None)
    execution_start: int | None = Field(repr=False, default=None)
    resource_usage: float | None = Field(repr=False, default=None)
    total_stages: int | None = Field(repr=False, default=None)
    total_rows_written: int | None = Field(repr=False, default=None)
    execution_end: int | None = Field(repr=False, default=None)
    duration: int | None = Field(repr=False, default=None)
    total_rows_read: int | None = Field(repr=False, default=None)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.job_run": {}}

    def __init__(
        self, platform: Optional["Platform"] = None, project: Optional["Project"] = None, **job_run_json: dict
    ) -> None:
        """The __init__ of the Job Run class.

        Args:
            platform: The Platform object.
            project: The Project object.
            job_run_json: The JSON for the Job Run.
        """
        super().__init__(**job_run_json)
        self._platform = platform
        self._project = project

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

    def cancel(self) -> requests.Response:
        """Stop already started Job Run.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
        """
        query_params = {
            "project_id": self._project.project_id,
        }

        return self._platform._job_api.cancel_job_run(  # noqa
            run_id=self.job_run_id, job_id=self.job_id, data=None, params=query_params
        )

    @property
    def logs(self) -> list[str]:
        """Retrieves runtime logs for a job run.

        Returns:
            A list containing runtime log entries that describe the job run execution.
            Each entry is a single log line from the UI.

        Raises:
            TypeError: If the provided job type is streaming.
        """
        if self.job_type.lower() == JobType.Streaming:
            raise TypeError(f"Job run logs property is currently not supported for {self.job_type} job type.")

        query_params = {
            "project_id": self._project.project_id,  # noqa
        }

        res = self._platform._job_api.get_job_run_logs(  # noqa
            run_id=self.job_run_id, job_id=self.job_id, params=query_params
        )
        logs_json = res.json()
        return logs_json.get("results", list())

    def refresh_status(self) -> requests.Response:
        """Updated status of a job."""
        res = None

        query_params = {
            "project_id": self._project.project_id,  # noqa
            "userfs": False,
        }
        try:
            res = self._platform._job_api.get_status(run_id=self.job_run_id, job_id=self.job_id, params=query_params)
            self.state = JobRunState(res.json()["entity"]["job_run"]["state"])
        except IbmCloudApiException:
            response = self._platform._job_api.get_job_run(self.job_run_id, self.job_id, query_params)
            self.state = JobRunState(response.json()["entity"]["job_run"]["state"])

        return res


class JobRuns(CollectionModel):
    """Collection of Job Run instances."""

    def __init__(self, platform: "Platform", project: "Project", job_id: str) -> None:
        """The __init__ of the JobRuns class.

        Args:
            platform: The Platform object.
            project: Instance of Project in which job run was created.
            job_id: ID of Job for which runs was stared.
        """
        super().__init__(platform)
        self.unique_id = "job_run_id"
        self._project = project
        self._job_id = job_id

    @override
    def __len__(self) -> int:
        query_params = {
            "project_id": self._project.project_id,
            "limit": 1,  # Use lowest `limit` since we need only `total_rows`
        }
        res = self._platform._job_api.get_job_runs(params=query_params, job_id=self._job_id)
        res_json = res.json()
        return res_json["total_rows"]

    def _request_parameters(self) -> list:
        request_params = []
        content_string = self._platform._job_api.get_swagger().text
        request_path = f"/{self._platform._job_api.url_path_common_core}/{{job_id}}/runs"
        data = yaml.safe_load(content_string)
        param_locations = data["paths"][request_path]["get"]["parameters"]
        for param_location in param_locations:
            request_params.append(param_location["name"])
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": self._project.project_id,
            "space_id": None,
            "states": None,
            "limit": 100,
            "next": None,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)

        if isinstance(request_params_unioned.get("states"), list):
            request_params_unioned["states"] = ",".join(request_params_unioned.get("states"))

        # Based on APISpec, query param `next` expect JSON string of `next` from previous call
        if isinstance(request_params_unioned.get("next"), dict):
            request_params_unioned["next"] = json.dumps(request_params_unioned["next"])

        if "job_run_id" in request_params:
            response_json = self._platform._job_api.get_job_run(
                run_id=request_params["job_run_id"],
                job_id=self._job_id,
                params={k: v for k, v in request_params_unioned.items() if v is not None},
            ).json()
            response = {"results": [response_json]}
        else:
            response = self._platform._job_api.get_job_runs(
                params={k: v for k, v in request_params_unioned.items() if v is not None}, job_id=self._job_id
            ).json()

        return CollectionModelResults(
            response,
            JobRun,
            "next",
            "next",
            "results",
            {"platform": self._platform, "project": self._project},
        )


class JobType(str, Enum):
    """Internal enum for asset/job type constants to replace hardcoded strings."""

    Streaming = "streamsets_flow"
    DataStage = "data_intg_flow"


class JobMetadata(BaseModel):
    """Model representing metadata for a job."""

    name: str = Field(repr=True)
    description: str | None = Field(repr=False, default="")
    asset_id: str = Field(frozen=True, repr=False)
    owner_id: str = Field(frozen=True, repr=False)
    version: int = Field(repr=True)

    _expose: bool = PrivateAttr(default=False)


class Job(BaseModel):
    """The model for CPD Job."""

    metadata: JobMetadata = Field(repr=True)

    asset_ref: str | None = Field(default=None, frozen=True, repr=False)
    job_id: str = Field(
        repr=True, default_factory=lambda fields: fields["metadata"].asset_id, frozen=True, exclude=True
    )
    job_type: str = Field(frozen=True, repr=False, alias="asset_ref_type")
    configuration: JobConfiguration = Field(repr=False)
    last_run_status_timestamp: int = Field(frozen=True, repr=False)
    future_scheduled_runs: list = Field(repr=False)
    enable_notifications: bool = Field(repr=False)
    project_name: str = Field(frozen=True, repr=True)
    schedule: str | None = Field(repr=False, default=None)
    schedule_info: ScheduleInfo | None = Field(repr=False, default=None)
    schedule_id: str = Field(frozen=True, repr=False)
    schedule_creator_id: str = Field(frozen=True, repr=False)
    job_parameters: list[JobParameter] | None = Field(default=None, repr=False)
    parameter_sets: list[ParameterSet] | None = Field(default=None, repr=False)
    retention_policy: RetentionPolicy | None = Field(default=None, repr=False)
    notification_types: NotificationTypes | None = Field(default=None, repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.job": {}}

    def __init__(
        self, platform: Optional["Platform"] = None, project: Optional["Project"] = None, **job_json: dict
    ) -> None:
        """The __init__ of the Job class.

        Args:
            platform: The Platform object.
            project: The Project object.
            job_json: The JSON for the Job.
        """
        super().__init__(**job_json)
        self._platform = platform
        self._project = project
        self._origin = self.model_dump()

    @staticmethod
    def _create(
        project: "Project",
        name: str,
        flow: Flow,
        configuration: dict[str, Any] | None = None,
        description: str | None = None,
        job_parameters: dict[str, Any] | None = None,
        retention_policy: dict[str, int] | None = None,
        notification_types: dict[str, bool] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
        schedule: str | None = None,
        schedule_info: dict[str, Any] | None = None,
    ) -> "Job":
        payload_extender_registry: dict[type[Flow], PayloadExtender] = {
            StreamingFlow: StreamingFlowPayloadExtender(),
            BatchFlow: BatchFlowPayloadExtender(),
        }

        query_params = {"project_id": project.project_id}

        new_job = {
            "name": name,
            "description": description,
            "configuration": dict(),
            "schedule": schedule,
        }

        payload_extender = payload_extender_registry.get(type(flow), DefaultFlowPayloadExtender())
        new_job = payload_extender.extend(new_job, flow)

        # Remove keys with `None` values, since endpoint does not allow
        # JSON null for fields.
        new_job = {k: v for k, v in new_job.items() if v is not None}

        if configuration:
            new_job["configuration"] = configuration
        elif isinstance(flow, BatchFlow) and flow.configuration:
            new_job |= flow.configuration.as_dict()

        # json.dumps can not serialize Pydantic models so we must call `model_dump` manually
        if parameter_sets:
            new_job["parameter_sets"] = parameter_sets
        elif hasattr(flow, "parameter_sets") and len(flow.parameter_sets):
            new_job["parameter_sets"] = flow._get_parameter_sets_list()

        if job_parameters:
            new_job["job_parameters"] = [{"name": k, "value": v} for k, v in job_parameters.items()]
        elif isinstance(flow, BatchFlow) and flow.job_parameters:
            new_job["job_parameters"] = flow.job_parameters

        if retention_policy:
            new_job["retention_policy"] = retention_policy

        if notification_types:
            new_job["notification_types"] = notification_types

        if schedule_info:
            new_job["schedule_info"] = schedule_info

        data = {"job": new_job}
        res = project._platform._job_api.create_job(  # noqa
            data=json.dumps(data), params=query_params
        )
        job_json = res.json()
        return Job(platform=project._platform, project=project, **job_json)

    def _update(self) -> requests.Response:
        query_params = {
            "project_id": self._project.project_id,
        }
        payload = prepare_json_patch_payload(self.origin, self.model_dump())
        return self._platform._job_api.update_job(  # noqa
            job_id=self.job_id, data=payload, params=query_params
        )

    def _delete(self) -> requests.Response:
        query_params = {"project_id": self._project.project_id}
        return self._platform._job_api.delete_job(  # noqa
            job_id=self.job_id, params=query_params
        )

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

    @property
    def job_runs(self) -> JobRuns:
        """Returns a list of Job Runs of the job.

        Returns:
            A list of jobs runs for the given job.
        """
        return JobRuns(platform=self._platform, project=self._project, job_id=self.job_id)

    @property
    def name(self) -> str:
        """Returns name of job."""
        return self.metadata.name

    @name.setter
    def name(self, name: str) -> None:
        """Sets name of job."""
        self.metadata.name = name

    @property
    def description(self) -> str:
        """Returns description of job."""
        return self.metadata.description

    @description.setter
    def description(self, desc: str) -> None:
        """Sets description of job."""
        self.metadata.description = desc

    @property
    def version(self) -> str:
        """Returns version of job."""
        return self.metadata.version

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

    def delete_job_run(self, job_run: JobRun) -> requests.Response:
        """Delete given run of job.

        Args:
            job_run: Instance of a Job Run to delete.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
            If the code is 202, then the operation is in progress.
        """
        query_params = {
            "project_id": self._project.project_id,  # noqa
        }
        return self._platform._job_api.delete_job_run(  # noqa
            run_id=job_run.job_run_id, job_id=self.job_id, params=query_params
        )

    def start(
        self,
        name: str,
        description: str,
        configuration: dict[str, Any] | None = None,
        job_parameters: dict[str, Any] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
    ) -> JobRun:
        """Create Job Run for given configuration.

        Args:
            name: Name for a Job Run.
            description: Description for a Job Run.
            configuration: Environment variables.
            job_parameters: Parameters use internally by a Job.
            parameter_sets: Parameter sets for a Job Run.

        Returns:
            An instance of a Job Run.
        """
        query_params = {
            "project_id": self._project.project_id,  # noqa
        }

        new_data = {
            "name": name,
            "description": description,
        }

        if configuration:
            new_data["configuration"] = configuration

        if job_parameters:
            new_data["job_parameters"] = [{"name": k, "value": v} for k, v in job_parameters.items()]

        if parameter_sets:
            new_data["parameter_sets"] = parameter_sets

        data = {"job_run": new_data}
        res = self._platform._job_api.create_job_run(  # noqa
            job_id=self.job_id, data=json.dumps(data), params=query_params
        )
        job_run_json = res.json()
        return JobRun(platform=self._platform, project=self._project, **job_run_json)

    def reset_offset(self) -> requests.Response:
        """This method is intended to clear the current offset associated with a job.

        Returns:
            The HTTP response.

        Raises:
            TypeError: If the provided job type is not streaming.
        """
        if self.job_type.lower() != JobType.Streaming:
            raise TypeError(f"The reset_offset method is not supported for {self.job_type} job type.")

        query_params = {
            "project_id": self._project.project_id,
        }
        payload = json.dumps([{"op": "replace", "path": "/entity/job/configuration/offset", "value": None}])
        return self._platform._job_api.update_job(  # noqa
            job_id=self.job_id, data=payload, params=query_params
        )

    _SENTINEL: ClassVar = object()

    def edit_configuration(
        self,
        environment: str = _SENTINEL,
        warn_limit: int = _SENTINEL,
        retention_days: int = _SENTINEL,
        retention_amount: int = _SENTINEL,
        parameter_value_sets: list[tuple[str, str]] = _SENTINEL,
        job_parameters: list[tuple[str, str]] = _SENTINEL,
        schedule: Schedule = _SENTINEL,
        notify_success: bool = _SENTINEL,
        notify_warning: bool = _SENTINEL,
        notify_failure: bool = _SENTINEL,
    ) -> requests.Response:
        """This method edits the configuration of a job.

        It uses a sentinel object to make sure that the arguments the user
        explicitly change are the only ones that are affected.
        """
        if isinstance(retention_days, int) and isinstance(retention_amount, int):
            raise ValueError("Parameters retention_days and retention_amount must not both be specified")
        payload = []
        # Check if environment has been changed
        if environment is not self._SENTINEL or warn_limit is not self._SENTINEL:
            if environment is not self._SENTINEL:
                self.configuration.env_id = environment + "-" + self._project.project_id
            # Check if warn limits have been changed
            if warn_limit is not self._SENTINEL:
                self.configuration.flow_limits = {"warn_limit": warn_limit}
            payload.append(self._format_payload_item("add", "configuration"))

        # Check if retention has been changed
        if retention_days is not self._SENTINEL:
            if self.retention_policy:
                self.retention_policy.days = retention_days
                self.retention_policy.amount = None
            else:
                self.retention_policy = RetentionPolicy(days=retention_days)

            payload.append(self._format_payload_item("add", "retention_policy"))
        if retention_amount is not self._SENTINEL:
            if self.retention_policy:
                self.retention_policy.amount = retention_amount
                self.retention_policy.days = None
            else:
                self.retention_policy = RetentionPolicy(amount=retention_amount)

            payload.append(self._format_payload_item("add", "retention_policy"))

        # Check if value sets have been given
        if parameter_value_sets is not self._SENTINEL:
            for parameter_value in parameter_value_sets:
                for param_val in self.parameter_sets or []:
                    if param_val.name == parameter_value[0]:
                        param_val.value_set = parameter_value[1]

            payload.append(self._format_payload_item("add", "parameter_sets"))

        # Check if job parameters have been given
        if job_parameters is not self._SENTINEL:
            if not self.job_parameters:
                self.job_parameters = []
            for job_parameter in job_parameters:
                self.job_parameters.append(JobParameter(name=job_parameter[0], value=job_parameter[1]))
            payload.append(self._format_payload_item("add", "job_parameters"))
        # Check if notifications have been changed
        if (
            notify_success is not self._SENTINEL
            or notify_warning is not self._SENTINEL
            or notify_failure is not self._SENTINEL
        ):
            if not self.notification_types:
                self.notification_types = NotificationTypes()
            if notify_success is not self._SENTINEL:
                self.notification_types.success = notify_success
            if notify_warning is not self._SENTINEL:
                self.notification_types.warning = notify_warning
            if notify_failure is not self._SENTINEL:
                self.notification_types.failure = notify_failure

            payload.append(self._format_payload_item("add", "notification_types"))

        # Check if schedule has been changed
        if schedule is not self._SENTINEL:
            self._process_schedule(schedule)
            payload.append(self._format_payload_item("add", "schedule"))
            payload.append(self._format_payload_item("add", "schedule_info"))

        data = str(payload).replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
        return self._platform._job_api.update_job(  # noqa
            job_id=self.job_id,
            data=data,
            params={
                "project_id": self._project.project_id,
            },
        )

    def _format_payload_item(self, op: str, field: str) -> dict:
        """Format the values of a field for the update payload."""
        if field == "schedule":
            return {"op": op, "path": f"/entity/job/{field}", "value": self.schedule}
        elif field == "parameter_sets":
            return {
                "op": op,
                "path": f"/entity/job/{field}",
                "value": [paramset.model_dump() for paramset in self.parameter_sets],
            }
        elif field == "job_parameters":
            return {
                "op": op,
                "path": f"/entity/job/{field}",
                "value": [job_parameter.model_dump() for job_parameter in self.job_parameters],
            }
        return {
            "op": op,
            "path": f"/entity/job/{field}",
            "value": self.__getattribute__(field).model_dump(exclude_unset=True),
        }

    def _process_schedule(self, schedule: Schedule) -> None:
        """Process a Schedule object into Job.schedule and Job.schedule_info fields."""
        if not self.schedule_info:
            self.schedule_info = ScheduleInfo()

        if schedule.start_date:
            self.schedule_info.start_on = schedule.start_date.replace(second=0, microsecond=0).timestamp() * 1000
        else:
            self.schedule_info.start_on = None
        if schedule.end_date:
            self.schedule_info.end_on = schedule.end_date.replace(second=0, microsecond=0).timestamp() * 1000
        else:
            self.schedule_info.end_on = None

        self.schedule_info.repeat = False
        if schedule.repeat_mode is not None:
            # Check which repeat type is being used
            self.schedule_info.repeat = True
            if schedule.repeat_mode == "minutely":
                if not isinstance(schedule.repeat_value, int):
                    raise ValueError("Repeat_value must be an int if repeat_mode is minutely")
                self.schedule = f"*/{schedule.repeat_value} * * * *"
            elif schedule.repeat_mode == "hourly":
                if not isinstance(schedule.repeat_value, int):
                    raise ValueError("Repeat_value must be an int if repeat_mode is hourly")
                self.schedule = f"{schedule.repeat_value} * * * *"
            elif schedule.repeat_mode == "daily":
                if not isinstance(schedule.repeat_value, datetime.time):
                    raise ValueError("Repeat_value must be a datetime.time if repeat_mode is daily")
                temp_datetime = datetime.datetime.combine(datetime.date(2011, 1, 1), schedule.repeat_value)
                utc_datetime = temp_datetime.astimezone(datetime.timezone.utc)
                self.schedule = f"{utc_datetime.minute} {utc_datetime.hour} * * *"
            elif schedule.repeat_mode == "weekly":
                if not isinstance(schedule.repeat_value, tuple):
                    raise ValueError("Repeat_value must be a tuple of (day of week, time) if repeat_mode is weekly")
                if not isinstance(schedule.repeat_value[1], datetime.time):
                    raise ValueError("Repeat_value's second item must be a datetime.time")
                try:
                    day_of_week_int = _DAY_OF_WEEK_TO_INT[schedule.repeat_value[0].upper()]
                except ValueError:
                    print("First value of tuple must be a day of the week")
                temp_datetime = datetime.datetime.combine(datetime.date(2011, 1, 1), schedule.repeat_value[1])
                utc_datetime = temp_datetime.astimezone(datetime.timezone.utc)
                self.schedule = f"{utc_datetime.minute} {utc_datetime.hour} * * {day_of_week_int}"
            elif schedule.repeat_mode == "monthly":
                if not isinstance(schedule.repeat_value, tuple):
                    raise ValueError("Repeat_value must be a tuple of (day of month, time) if repeat_mode is monthly")
                if not isinstance(schedule.repeat_value[0], int):
                    raise ValueError(
                        "Repeat_value's first item must be an int indicating day of month if repeat_mode is monthly"
                    )
                if not isinstance(schedule.repeat_value[1], datetime.time):
                    raise ValueError("Repeat_value's second item must be a datetime.time if repeat_mode is monthly")
                temp_datetime = datetime.datetime.combine(datetime.date(2011, 1, 1), schedule.repeat_value[1])
                utc_datetime = temp_datetime.astimezone(datetime.timezone.utc)
                self.schedule = f"{utc_datetime.minute} {utc_datetime.hour} {schedule.repeat_value[0]} * *"
            else:
                raise ValueError("Repeat_mode must be one of these values: [minutely, hourly, daily, weekly, monthly]")

            # Check if there are excluded days
            if schedule.exclude_days:
                if schedule.repeat_mode in ["weekly", "monthly"]:
                    raise ValueError(f"Cannot exclude days when repeat_mode is {schedule.repeat_mode}")
                days = [0, 1, 2, 3, 4, 5, 6]
                included_days = [day for day in days if day not in schedule.exclude_days]
                replacements = str.maketrans({"[": "", "]": "", " ": ""})
                self.schedule = self.schedule[:-1] + str(included_days).translate(replacements)

        else:
            self.schedule = None
        return


class Jobs(CollectionModel):
    """Collection of Job instances."""

    def __init__(self, platform: "Platform", project: "Project") -> None:
        """The __init__ of the Jobs class.

        Args:
            platform: The Platform object.
            project: Instance of Project in which job was created.
        """
        super().__init__(platform)
        self.unique_id = "job_id"
        self._project = project

    @override
    def __len__(self) -> int:
        query_params = {
            "project_id": self._project.project_id,
            "limit": 1,  # Use lowest `limit` since we need only `total_rows`
        }
        res = self._platform._job_api.get_jobs(params=query_params)
        res_json = res.json()
        return res_json["total_rows"]

    def _request_parameters(self) -> list:
        request_params = ["job_id"]
        content_string = self._platform._job_api.get_swagger().text
        request_path = f"/{self._platform._job_api.url_path_common_core}"
        data = yaml.safe_load(content_string)
        param_locations = data["paths"][request_path]["get"]["parameters"]
        for param_location in param_locations:
            request_params.append(param_location["name"])
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": self._project.project_id,
            "space_id": None,
            "asset_ref": None,
            "asset_ref_type": None,
            "run_id": None,
            "limit": 100,
            "next": None,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(self._remap_request_params(request_params))

        # Based on APISpec, query param `next` expect JSON string of `next` from previous call
        if isinstance(request_params_unioned.get("next"), dict):
            request_params_unioned["next"] = json.dumps(request_params_unioned["next"])

        if "job_id" in request_params:
            response_json = self._platform._job_api.get_job(
                job_id=request_params["job_id"],
                params={k: v for k, v in request_params_unioned.items() if v is not None},
            ).json()
            response = {"results": [response_json]}
        else:
            response = self._platform._job_api.get_jobs(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        return CollectionModelResults(
            response,
            Job,
            "next",
            "next",
            "results",
            {"platform": self._platform, "project": self._project},
        )

    def _remap_request_params(self, request_params: dict[str, Any]) -> dict[str, Any]:
        """Remaps user-friendly filter names to accepted by endpoint.

        Args:
            request_params: Query filters specified by user.

        Returns:
            A dictionary with remapped filters names.
        """
        mapping = {"job_type": "asset_ref_type"}
        result = dict()

        for k, v in request_params.items():
            key = mapping.get(k, k)
            result[key] = v

        return result
