#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Project Models."""

import io
import json
import os
import requests
import warnings
from ibm_watsonx_data_integration.common.exceptions import CloudObjectStorageNotFoundError
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.common.utils import get_params_from_swagger
from ibm_watsonx_data_integration.cpd_models import (
    AccessGroup,
    AccessGroupOnPrem,
    Connection,
    Connections,
    DatasourceType,
    Job,
    Jobs,
    ProjectCollaborator,
    ProjectCollaborators,
    ServiceID,
    TrustedProfile,
    UserProfile,
    UserProfileOnPrem,
)
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow
from ibm_watsonx_data_integration.cpd_models.flows_model import Flows
from ibm_watsonx_data_integration.cpd_models.parameter_set_model import ParameterSet, ParameterSets
from ibm_watsonx_data_integration.cpd_models.project_collaborator_model import CollaboratorRole
from ibm_watsonx_data_integration.services.datastage.models.flow.subflow import Subflow, Subflows
from ibm_watsonx_data_integration.services.streamsets.models import (
    Engine,
    Engines,
    Environment,
    Environments,
    StreamingConnection,
    StreamingEngineVersion,
    StreamingFlow,
)
from ibm_watsonx_data_integration.services.streamsets.models.flow_model import FlowValidationError
from pathlib import Path
from pydantic import ConfigDict, Field, PrivateAttr, TypeAdapter
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class ProjectMetadata(BaseModel):
    """Model for metadata in a project."""

    guid: str = Field(repr=False)
    url: str = Field(repr=False)
    created_at: str | None = Field(repr=False)
    updated_at: str | None = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Storage(BaseModel):
    """Model for Storage details in a project."""

    type: str
    guid: str = Field(frozen=True)
    properties: dict[str, Any] | None = Field(default=[], repr=False)
    _expose: bool = PrivateAttr(default=False)


class Scope(BaseModel):
    """Model for Scope details in a project."""

    bss_account_id: str = Field(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Project(BaseModel):
    """The Model for Projects."""

    metadata: ProjectMetadata = Field(repr=True)

    name: str = Field(repr=True)
    description: str | None = Field(default=None, repr=False)
    project_id: str = Field(
        repr=True, default_factory=lambda fields: fields["metadata"].guid, frozen=True, exclude=True
    )
    type: str | None = Field(repr=False)
    generator: str | None = Field(repr=False)
    public: bool | None = Field(repr=False)
    creator: str | None = Field(repr=False)
    tags: list | None = Field(default_factory=list, repr=False)

    storage: Storage | None = Field(repr=False)
    scope: Scope | None = Field(repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}

    def __init__(self, platform: Optional["Platform"] = None, **project_json: dict) -> None:
        """The __init__ of the Project class.

        Args:
            platform: The Platform object.
            project_json: The JSON for the Service.
        """
        super().__init__(**project_json)
        self._platform = platform
        self._inital_tags = [] if not hasattr(self, "tags") else list(self.tags)

    def _update_tags(self) -> None:
        """Updates tags of the Project."""
        initial_tags = set(self._inital_tags)
        current_tags = set(self.tags)

        body = []

        tags_to_delete = initial_tags - current_tags
        if tags_to_delete:
            body.append({"op": "remove", "tags": list(tags_to_delete)})

        tags_to_add = current_tags - initial_tags
        if tags_to_add:
            body.append({"op": "add", "tags": list(tags_to_add)})

        if body:
            self._inital_tags = self.tags
            self._platform._project_api.update_tags(self.project_id, json.dumps(body))

    @staticmethod
    def _create(
        platform: "Platform",
        name: str,
        description: str = "",
        tags: list = None,
        public: bool = False,
        project_type: str = "wx",
        on_prem: bool = False,
    ) -> "Project":
        data = {
            "name": name,
            "description": description,
            "generator": "watsonx-di-sdk",
            "public": public,
            "tags": ["sdk-tags"] if not tags else tags,
            "type": project_type,
            "storage": {},
        }

        if on_prem:
            data["storage"].update({"type": "assetfiles"})
        else:
            cloud_storage = Project._get_cloud_storage(platform=platform)
            cloud_storage_guid = cloud_storage["guid"]
            cloud_storage_id = cloud_storage["id"]

            data["storage"].update(
                {
                    "type": "bmcos_object_storage",
                    "guid": cloud_storage_guid,
                    "resource_crn": cloud_storage_id,
                }
            )

        response = platform._project_api.create_project(json.dumps(data))
        location = response.json()["location"]
        project_id = location.split("/")[-1]

        project_json = platform._project_api.get_project(project_id).json()
        return Project(platform=platform, **project_json)

    def _update(self) -> requests.Response:
        # Update tags
        self._update_tags()

        # Update rest of project
        data = {"name": self.name, "description": self.description, "public": self.public}

        project_json = self.model_dump()
        if "catalog" in project_json:
            data["catalog"] = {"guid": project_json["catalog"]["guid"], "public": project_json["catalog"]["public"]}

        data = json.dumps(data)
        return self._platform._project_api.update_project(id=self.project_id, data=data)

    def _delete(self) -> requests.Response:
        return self._platform._project_api.delete_project(self.project_id)

    @staticmethod
    def _get_cloud_storage(platform: "Platform") -> list:
        search_response = platform._global_search_api.get_resources(
            json.dumps({"query": "region:global AND service_name:cloud-object-storage", "fields": ["*"]})
        ).json()
        items = search_response.get("items", [])
        if not items:
            raise CloudObjectStorageNotFoundError("Cloud Object Storage does not exist. Cannot proceed.")

        return items[0]["doc"]

    @property
    def jobs(self) -> Jobs:
        """Retrieves jobs associated with the project.

        Returns:
            A list of Jobs within the project.
        """
        return Jobs(platform=self._platform, project=self)

    def create_job(
        self,
        name: str,
        flow: Flow,
        configuration: dict[str, Any] | None = None,
        description: str | None = None,
        job_parameters: dict[str, Any] | None = None,
        retention_policy: dict[str, int] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
        schedule: str | None = None,
        schedule_info: dict[str, Any] | None = None,
    ) -> Job:
        """Create Job for given asset.

        Args:
            name: Name for a Job.
            flow: A reference to the flow for which the job will be created.
            configuration: Environment variables for a Job.
            description: Job description.
            job_parameters: Parameters use internally by a Job.
            retention_policy: Retention policy for a Job.
            parameter_sets: Parameter sets for a Job.
            schedule: Crone string.
            schedule_info: Schedule info for a Job.

        Returns:
            A Job instance.

        Raises:
            TypeError: If both asset_ref and asset_ref_type are provided, or if neither is provided
        """
        return Job._create(
            self,
            name,
            flow,
            configuration,
            description,
            job_parameters,
            retention_policy,
            parameter_sets,
            schedule,
            schedule_info,
        )

    def delete_job(self, job: Job) -> requests.Response:
        """Allows to delete specified Job within project.

        Args:
            job: Instance of a Job to delete.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
        """
        return job._delete()

    def update_job(self, job: Job) -> requests.Response:
        """Allows to update specified Job within a project.

        Args:
            job: Instance of a Job to update.

        Returns:
            A HTTP response. If it is 200, then the operation completed successfully.
        """
        return job._update()

    def list_batch_environments(self) -> list[str]:
        """Lists batch environments within a project.

        Returns:
            List of internal names of environments.
        """
        return [
            entry["metadata"]["name"]
            for entry in self._platform._project_api.get_batch_environments().json()["resources"]
        ]

    def get_batch_environment(self, display_name: str) -> str:
        """Retrieve a batch environment by its display name.

        Returns:
            Internal name of the environment with the display name.
        """
        for entry in self._platform._project_api.get_batch_environments().json()["resources"]:
            if entry["entity"]["environment"]["display_name"] == display_name:
                return entry["metadata"]["name"]
        return ValueError(f"Could not find environment with display name {display_name}")

    @property
    def environments(self) -> Environments:
        """Retrieves environments associated with the project.

        Returns:
            A list of Environments within the project.
        """
        return Environments(platform=self._platform, project=self)

    def create_environment(
        self,
        *,
        name: str,
        engine_version: StreamingEngineVersion | str | None = None,
        description: str = None,
        engine_type: str = "data_collector",
        engine_properties: dict = None,
        log4j2_properties: dict = None,
        external_resource_asset: dict = None,
        stage_libs: list = None,
        jvm_options: list = None,
        max_cpu_load: float = None,
        max_memory_used: float = None,
        max_jobs_running: int = None,
        engine_heartbeat_interval: int = None,
        cpus_to_allocate: float = None,
        custom_cert: str | None = None,
    ) -> Environment:
        """Allows to create a new Environment within project.

        All of not set parameters will be skipped and set with default values provided by backed.

        Args:
            name: Name of the environment.
            description: Description of the environment.
            engine_type: Type of the engine.
            engine_version: Version of the engine. Default is the latest engine version.
            engine_properties: Properties of the engine.
            external_resource_asset: External resources.
            log4j2_properties: Log4j2 properties.
            stage_libs: Stage libraries.
            jvm_options: JVM options.
            max_cpu_load: Maximum CPU load.
            max_memory_used: Maximum memory used.
            max_jobs_running: Maximum jobs running.
            engine_heartbeat_interval: Engine heartbeat interval.
            cpus_to_allocate: Number of CPU used.
            custom_cert: Custom cert to add to the engine truststore.

        Returns:
            The created environment.
        """
        return Environment._create(
            self,
            name,
            engine_version,
            description,
            engine_type,
            engine_properties,
            log4j2_properties,
            external_resource_asset,
            stage_libs,
            jvm_options,
            max_cpu_load,
            max_memory_used,
            max_jobs_running,
            engine_heartbeat_interval,
            cpus_to_allocate,
            custom_cert=custom_cert,
        )

    def delete_environment(self, environment: Environment) -> requests.Response:
        """Allows to delete specified Environment within a Project.

        Args:
            environment: Instance of an Environment to delete.

        Returns:
            A HTTP response.
        """
        return environment._delete()

    def delete_environments(self, *environments: Environment) -> requests.Response:
        """Allows to delete multiple Environments within a Project.

        Args:
            environments: Instances of an Environment to delete.

        Returns:
            A HTTP response.
        """
        return Environment._bulk_delete(self, *environments)

    def update_environment(self, environment: Environment) -> requests.Response:
        """Allows to update specified Environment within a Project.

        Args:
            environment: Instance of an Environment to update.

        Returns:
            A HTTP response.
        """
        return environment._update()

    @property
    def flows(self) -> Flows:
        """Returns Flows from the Project."""
        return Flows(project=self)

    def delete_flow(self, flow: Flow) -> requests.Response:
        """Delete a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        return flow._delete()

    def create_flow(
        self, name: str, environment: Environment | None = None, description: str = "", flow_type: str = "streaming"
    ) -> Flow:
        """Creates a Flow.

        Args:
            name: The name of the flow.
            environment: The environment which will be used to run this flow.
            description: The description of the flow.
            flow_type: The type of flow (must be registered in Flow.flow_registry).

        Returns:
            The created Flow subclass instance (StreamingFlow by default).

        """
        try:
            flow = Flow._flow_registry[flow_type]
        except ValueError:
            raise TypeError(f"Flow type '{flow_type}' is not supported. Available: {list(Flow._flow_registry)}")

        flow = flow._create(
            project=self, name=name, environment=environment, description=description, flow_type=flow_type
        )
        return flow

    def update_flow(self, flow: Flow) -> requests.Response:
        """Update a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        return flow._update()

    def duplicate_flow(self, flow: Flow, name: str, description: str = "", number_of_copies: int = 1) -> Flow:
        """Duplicate a Flow.

        Args:
            flow: The Flow.
            name: The name of the flow.
            description: The description of the flow.
            number_of_copies: The number of copies to make.

        Returns:
            A copy of passed flow.
        """
        original_copy = flow._duplicate(name, description)
        for i in range(1, number_of_copies):
            flow._duplicate(f"{name}_{str(i)}", description)
        return original_copy

    def validate_flow(self, flow: StreamingFlow) -> list[FlowValidationError]:
        """Validates a flow.

        Args:
            flow: The Flow to validate.

        Returns:
            A `list` of `FlowValidationError` containing issues.
        """
        warnings.warn(
            "Project.validate_flow() is now deprecated. Use StreamingFlow.validate() instead.", DeprecationWarning
        )
        return flow.validate()

    def export_streaming_flows(
        self,
        flows: list[StreamingFlow] | StreamingFlow | Flows,
        with_plain_text_credentials: bool = False,
        destination: str | Path = "flows.zip",
        stream: bool = True,
    ) -> Path:
        """Export Streaming Flows.

        Args:
            with_plain_text_credentials: A boolean to allow plain text credentials to be exported.
            flows: An individual Flow or a list of Flows to be exported.
            destination: The path to which the zip file should be saved to.
            stream: Whether to stream the response in chunks.

        Returns:
            A string with the path to which the zip file was saved.
        """
        flow_ids = []
        if type(flows) is StreamingFlow:
            flow_ids.append(flows.flow_id)
        elif type(flows) is list:
            for flow in flows:
                if type(flow) is StreamingFlow:
                    flow_ids.append(flow.flow_id)
                else:
                    raise TypeError("flows is not the correct type")
        elif type(flows) is Flows:
            for flow in flows:
                flow_ids.append(flow.flow_id)
        else:
            raise TypeError("flows is not the correct type")

        query_params = {
            "project_id": self.project_id,
            "with_plain_text_credentials": with_plain_text_credentials,
            "flow_ids": flow_ids,
        }
        response = self._platform._streaming_flow_api.export_streaming_flow(params=query_params, stream=stream)

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open(mode="wb", buffering=io.DEFAULT_BUFFER_SIZE) as f:
            chunk_size = io.DEFAULT_BUFFER_SIZE
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

        return path

    def import_streaming_flows(
        self, source: str | Path, conflict_resolution: str
    ) -> list[StreamingFlow] | StreamingFlow:
        """Import Streaming Flows.

        Args:
            source: The path to the zip file of flows to be imported.
            conflict_resolution: The desired behavior to handle duplicate flows.

        Returns:
            An individual streaming flow or a list of all streaming flows imported.

        Raises:
            FileNotFoundError: If the provided source path does not exist.
            TypeError: If the flow is not imported successfully.

        """
        if os.path.exists(source):
            query_params = {"project_id": self.project_id, "conflict_resolution": conflict_resolution}
            with open(source, "rb") as zip_file:
                data = zip_file.read()
                response = self._platform._streaming_flow_api.import_streaming_flow(params=query_params, data=data)
        else:
            raise FileNotFoundError(f"The path '{source}' does not exist.")
        if response.status_code == 200:
            flow_jsons = response.json()["imported_flows"]
            if len(flow_jsons) == 1:
                return self.flows.get(name=flow_jsons[0]["name"])
            imported_flows = []
            for flow in flow_jsons:
                imported_flows.append(self.flows.get(name=flow["name"]))
            return imported_flows
        else:
            raise TypeError("Flow(s) not imported successfully.")

    @property
    def subflows(self) -> Subflows:
        """Returns Subflows from the Project."""
        return Subflows(project=self)

    def delete_subflow(self, subflow: Subflow) -> requests.Response:
        """Delete a subflow.

        Args:
            subflow: The Subflow object.

        Returns:
            A HTTP response.
        """
        if subflow.is_local:
            raise TypeError("Cannot delete a local subflow from a project.")

        return subflow._delete()

    def create_subflow(self, name: str, description: str = "") -> Subflow:
        """Creates a Subflow component in the project.

        Args:
            name: The name of the subflow.
            description: The description of the subflow.

        Returns:
            The created subflow object.

        """
        subflow = Subflow(project=self, name=name, description=description, is_local=False)._create()
        return subflow

    def update_subflow(self, subflow: Subflow) -> requests.Response:
        """Update a subflow.

        Args:
            subflow: The Subflow object.

        Returns:
            A HTTP response.
        """
        if subflow.is_local:
            raise TypeError("Cannot update a local subflow from a project. Use flow.update_subflow(s) instead.")

        return subflow._update()

    def duplicate_subflow(self, subflow: Flow, name: str, description: str = "") -> Subflow:
        """Duplicate a Flow.

        Args:
            subflow: The Subflow.
            name: The name of the subflow.
            description: The description of the subflow.

        Returns:
            A copy of passed subflow.
        """
        if subflow.is_local:
            raise TypeError(
                "Cannot duplicate a local subflow from the project-level. Use flow.duplicate_subflow(s) instead."
            )

        return subflow._duplicate(name, description)

    @property
    def engines(self) -> Engines:
        """Returns the engines associated with the Project."""
        return Engines(project=self)

    def get_engine(self, engine_id: str) -> Engine:
        """Retrieve an engine by its engine_id.

        Args:
            engine_id (str): The asset_id of the engine to retrieve.

        Returns:
            Engine: The retrieved engine.

        Raises:
            HTTPError: If the request fails.
        """
        query_params = {
            "project_id": self.project_id,
        }
        api_response = self._platform._engine_api.get_engine(engine_id=engine_id, params=query_params)
        return Engine(platform=self._platform, project=self, **api_response.json())

    def delete_engine(self, engine: Engine) -> requests.Response:
        """Allows to delete specified Engine within project.

        Args:
            engine: Instance of an Engine to delete.

        Returns:
            A HTTP response.
        """
        query_params = {"project_id": self.project_id}
        return self._platform._engine_api.delete_engine(engine_id=engine.engine_id, params=query_params)

    @property
    def connections(self) -> Connections:
        """Retrieves connections associated with the project.

        Returns:
            A Connections object.
        """
        return Connections(platform=self._platform, project=self)

    def create_connection(
        self,
        name: str,
        datasource_type: DatasourceType,
        description: str | None = None,
        properties: dict | None = None,
        test: bool = True,
    ) -> Connection:
        """Create a Connection.

        Args:
            name: name for the new connection.
            description: description for the new connection.
            datasource_type: type of the datasource.
            properties: properties of the new connection.
            test: whether to test the connection before saving it.
                  If true and validation cannot be estabilished, connection will not be saved.

        Returns:
            Created Connection object.
        """
        return Connection._create(self, name, datasource_type, description, properties, test)

    def delete_connection(self, connection: Connection) -> requests.Response:
        """Remove the Connection.

        Args:
            connection: connection to delete

        Returns:
            A HTTP response.
        """
        return connection._delete()

    def update_connection(self, connection: Connection, test: bool = True) -> requests.Response:
        """Update the Connection.

        Args:
            connection: connection to update
            test: whether to test the connection before saving it.
                  If true and validation cannot be estabilished, connection will not be saved.

        Returns:
            A HTTP response.
        """
        return connection._update(test=test)

    def copy_connection(self, connection: Connection) -> Connection:
        """Copy the Connection.

        Args:
            connection: connection to copy

        Returns:
            Copied Connection object.
        """
        return connection._copy()

    @property
    def parameter_sets(self) -> ParameterSets:
        """Retrieves parameter sets associated with the project.

        Returns:
            A ParameterSets object.
        """
        return ParameterSets(project=self)

    def create_parameter_set(
        self, name: str, description: str = "", parameters: list = [], value_sets: list = []
    ) -> ParameterSet:
        """Create a Parameter Set.

        Args:
            name: name for the new parameter set.
            description: description for the new parameter set.
            parameters: parameters for the new parameter set.
            value_sets: value sets for the new parameter set.

        Returns:
            Created ParameterSet object.
        """
        return ParameterSet._create(self, name, description, parameters, value_sets)

    def delete_parameter_set(self, parameter_set: ParameterSet) -> requests.Response:
        """Delete a Parameter Set.

        Args:
            parameter_set: Parameter set to delete

        Returns:
            A HTTP response.
        """
        return parameter_set._delete()

    def update_parameter_set(self, parameter_set: ParameterSet) -> requests.Response:
        """Update a Parameter Set.

        Args:
            parameter_set: Parameter set to update

        Returns:
            A HTTP response.
        """
        return parameter_set._update()

    def duplicate_parameter_set(self, parameter_set: ParameterSet) -> ParameterSet:
        """Duplicate a Parameter Set.

        Args:
            parameter_set: Parameter set to copy

        Returns:
            Duplicated ParameteSet Object
        """
        return parameter_set._duplicate()

    @property
    def collaborators(self) -> ProjectCollaborators:
        """Retrieves project members associated with the project.

        Returns:
            ProjectCollaborators object.
        """
        return ProjectCollaborators(self)

    def add_collaborators(
        self,
        collaborators: list[
            AccessGroup | ServiceID | TrustedProfile | UserProfile | AccessGroupOnPrem | UserProfileOnPrem
        ],
        *,
        role: CollaboratorRole,
    ) -> list[ProjectCollaborator]:
        """Adds a list of collaborators to the project.

        Args:t
            collaborators: list of collaborators to add
            role: role to assign members

        Returns:
            List of collaborators added.
        """
        if len(collaborators) == 0:
            raise ValueError("Cannot add an empty list of collaborators to the project")

        mapped_collaborators = []
        for member in collaborators:
            mapped_collaborators.append(member._to_collaborator(self, role).model_dump())

        response = self._platform._project_api.add_project_members(self.project_id, mapped_collaborators).json()
        return TypeAdapter(list[ProjectCollaborator]).validate_python(response["members"])

    def add_collaborator(
        self,
        collaborator: AccessGroup | ServiceID | TrustedProfile | UserProfile | AccessGroupOnPrem | UserProfileOnPrem,
        *,
        role: CollaboratorRole,
    ) -> ProjectCollaborator:
        """Adds a collaborator to the project.

        Args:
            collaborator: collaborator to add
            role: role to assign members

        Returns:
            ProjectCollaborator object.
        """
        if collaborator is None:
            raise ValueError("collaborator cannot be None")
        return self.add_collaborators([collaborator], role=role)[0]

    def remove_collaborators(self, collaborators: list[ProjectCollaborator]) -> requests.Response:
        """Removes collaborators from the project.

        Args:
            collaborators: collaborators to remove

        Returns:
            A HTTPResponse object.
        """
        user_names = [member.user_name for member in collaborators]
        if len(user_names) == 0:
            raise ValueError("Cannot remove an empty list of collaborators from the project")
        return self._platform._project_api.remove_project_members(self.project_id, user_names)

    def remove_collaborator(self, collaborator: ProjectCollaborator) -> requests.Response:
        """Removes a collaborator from the project.

        Args:
            collaborator: collaborator to remove

        Returns:
            A HTTPResponse object.
        """
        if collaborator is None:
            raise ValueError("collaborator cannot be None")
        return self.remove_collaborators([collaborator])

    def update_collaborators(self, collaborators: list[ProjectCollaborator]) -> list[ProjectCollaborator]:
        """Updates collaborators in the project.

        Args:
            collaborators: collaborators to update

        Returns:
            A list of updated members.
        """
        mapped_members = [member.model_dump(exclude={"type", "state"}) for member in collaborators]
        if len(mapped_members) == 0:
            raise ValueError("Cannot update a list of empty project collaborators")
        response = self._platform._project_api.update_project_members(self.project_id, mapped_members).json()
        return TypeAdapter(list[ProjectCollaborator]).validate_python(response["members"])

    def update_collaborator(self, collaborator: ProjectCollaborator) -> ProjectCollaborator:
        """Updates a collaborator in the project.

        Args:
            collaborator: collaborator to update

        Returns:
            An updated project collaborator.
        """
        if collaborator is None:
            raise ValueError("collaborator cannot be None")
        return self.update_collaborators([collaborator])[0]

    @property
    def _streaming_connections(self) -> list[StreamingConnection]:
        """Retrieves Streaming connections associated with the project.

        Returns:
            A list of StreamingConnection within the project.
        """
        connections_json = self._platform._streaming_flow_api.get_streaming_connections(
            params={
                "project_id": self.project_id,
            },
        ).json()

        return [
            StreamingConnection(
                platform=self._platform,
                project=self,
                **{
                    "entity": {
                        "datasource_type": connection["datasource_type"],
                        "name": connection["name"],
                    },
                    "metadata": {
                        "asset_id": connection["asset_id"],
                    },
                },
            )
            for connection in connections_json.get("connections", list())
        ]

    def _get_streaming_connection(
        self, connection_id: str, version: str | None = None, type: str | None = None
    ) -> StreamingConnection:
        """Retrieves Streaming connection by id associated with the project.

        Args:
            connection_id: Id of the connection asset to retrieve.
            version: Connection version.
            type: Connection type.

        Returns:
            Retrieved StreamingConnection object.
        """
        params = {
            "project_id": self.project_id,
        }
        if version:
            params["connection_version"] = version
        if type:
            params["connection_type"] = type

        connection_json = self._platform._streaming_flow_api.get_streaming_connection(
            connection_id=connection_id,
            params=params,
        ).json()

        # NOTE: connection_json has also 'alternative_mapping' reserved for future use
        #       this object is stripped for now as it is filled with nulls
        return StreamingConnection(platform=self._platform, project=self, **connection_json["connection"])


class Projects(CollectionModel):
    """Collection of Project instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Projects class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "project_id"

    def __len__(self) -> int:
        """Total amount of projects."""
        return self._platform._project_api.get_projects_total().json()["total"]

    def _request_parameters(self) -> list:
        request_params = ["project_id"]
        content_string = self._platform._project_api.get_swagger().content.decode("utf-8")
        request_path = f"/{self._platform._project_api.url_path}"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": None,
            "bss_acount_id": None,
            "type": None,
            "member": None,
            "roles": None,
            "tag_names": None,
            "name": None,
            "match": None,
            "project_ids": None,
            "include": "name,fields,members,tags,settings",
            "limit": 100,
            "bookmark": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        project_id = request_params_unioned.get("project_id")

        if project_id:
            response = self._platform._project_api.get_project(project_id).json()
            response = {"resources": [response]}
        else:
            response = self._platform._project_api.get_projects(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
        return CollectionModelResults(
            response,
            Project,
            "bookmark",
            "bookmark",
            "resources",
            {"platform": self._platform},
        )
