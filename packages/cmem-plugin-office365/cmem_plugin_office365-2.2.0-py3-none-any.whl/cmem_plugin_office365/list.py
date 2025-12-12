"""List files office plugin"""

from collections import OrderedDict
from collections.abc import Sequence
from typing import Any

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities, Entity, EntityPath, EntitySchema
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from office365.graph_client import GraphClient
from office365.runtime.client_object import ClientObject

from cmem_plugin_office365.autocompletion import (
    DriveDirectoryParameterType,
    FolderDirectoryParameterType,
    ResourceDirectoryParameterType,
)
from cmem_plugin_office365.retrieval import OfficeRetrieval

RESOURCE_CHOICE = OrderedDict({"personal": "Personal", "site": "Site"})
MAX_WORKERS = 32


def generate_schema() -> EntitySchema:
    """Generate the schema for entities"""
    return EntitySchema(
        type_uri="",
        paths=[
            EntityPath(path="type"),
            EntityPath(path="name"),
            EntityPath(path="web_url"),
            EntityPath(path="parent_reference"),
            EntityPath(path="microsoft_graph_download_url"),
            EntityPath(path="created_by"),
            EntityPath(path="created_date_time"),
            EntityPath(path="eTag"),
            EntityPath(path="id"),
            EntityPath(path="last_modified_by"),
            EntityPath(path="last_modified_date_time"),
            EntityPath(path="cTag"),
            EntityPath(path="size"),
        ],
    )


def setup_max_workers(max_workers: int) -> int:
    """Return the correct amount of workers"""
    if 0 < max_workers <= MAX_WORKERS:
        return max_workers
    raise ValueError("Range of max_workers exceeded")


@Plugin(
    label="List Office 365 Files",
    plugin_id="cmem_plugin_office365-List",
    description="List files from OneDrive or Sites",
    documentation="""
This workflow task creates a structured output from a specified Office 365 instance.
For this to work a registered app in Microsoft's Entra ID space is necessary.
Further information can be found [here](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).

After registering an application, it needs to be granted application wide API permissions:

- Files.Read.All
- Sites.Read.All

Admin consent is required to activate these permissions.
With this setup, anyone with the secret can access all users' OneDrives and all Sharepoint/Team
sites.

#### Important

Make sure only trusted admins can create or manage secrets!
Whoever holds the secrets has all the access to granted resources so best not to distribute
recklessly.
    """,
    icon=Icon(package=__package__, file_name="o365-list.svg"),
    actions=[
        PluginAction(
            name="preview_results", label="Preview results", description="Preview the results."
        )
    ],
    parameters=[
        PluginParameter(
            name="tenant_id",
            label="Tenant ID",
            description="ID of your tenant. Can be seen within your registered application",
        ),
        PluginParameter(
            name="client_id",
            label="Client ID",
            description="Client ID of your registered application.",
        ),
        PluginParameter(
            param_type=PasswordParameterType(),
            name="client_secret",
            label="Client secret",
            description="Client secret created withing your registered application.",
        ),
        PluginParameter(
            param_type=ChoiceParameterType(OrderedDict({"personal": "Personal", "site": "Site"})),
            name="type_resource",
            label="Type resource",
            description="The type of resource you want the data to be extracted from. "
            "This can either be a site or a users share",
        ),
        PluginParameter(
            name="target_resource",
            label="Target resource",
            description="Target resource which files will be listed from. This can either be a "
            "specific users share address or a microsoft site URL.",
            param_type=ResourceDirectoryParameterType("resource", "Resource"),
        ),
        PluginParameter(
            name="drives",
            label="Drives",
            description="A list of drives from the selected target resource.",
            param_type=DriveDirectoryParameterType("drives", "Drives"),
        ),
        PluginParameter(
            name="path",
            label="Directory path",
            description="The path of a directory that needs to be transformed. Includes all "
            "subdirectories by default",
            param_type=FolderDirectoryParameterType("path", "Path"),
        ),
        PluginParameter(
            name="regex",
            label="Regular expression",
            description="A regular expression performed on all the files within the selected path",
            default_value="^.*$",
        ),
        PluginParameter(
            name="no_subfolder",
            label="Exclude files in subfolders",
            description="A flag indicating if files should only be listed from subfolders or not.",
        ),
        PluginParameter(
            name="max_workers",
            label="Maximum amount of workers",
            description="Specifies the maximum number of threads used for parallel execution of "
            "the workflow. "
            "The default is 32, and the valid range is 1 to 32. "
            "Note: Due to known throttling limits imposed by Microsoft, running with high "
            "parallelism may cause errors. "
            "If you encounter issues, try reducing the number of threads to 1.",
            advanced=True,
            default_value=32,
        ),
    ],
)
class ListPlugin(WorkflowPlugin):
    """List Plugin Office 365"""

    def __init__(  # noqa: PLR0913
        self,
        tenant_id: str,
        client_id: str,
        client_secret: Password | str,
        type_resource: str,
        target_resource: str,
        drives: str,
        max_workers: int = 32,
        path: str = "",
        regex: str = "",
        no_subfolder: bool = False,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = (
            client_secret if isinstance(client_secret, str) else client_secret.decrypt()
        )
        self.path = path
        self.type_resource = RESOURCE_CHOICE[type_resource]
        self.target_resource = target_resource
        self.drives = drives
        self.regex = rf"{regex}"
        self.no_subfolder = no_subfolder
        self.max_workers = setup_max_workers(max_workers)
        self.client = GraphClient(tenant=tenant_id).with_client_secret(
            self.client_id, self.client_secret
        )
        self.drive = self.create_drive()
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = FixedSchemaPort(schema=generate_schema())

    def preview_results(self) -> str:
        """Preview the result of the execution"""
        files: list[Any] = []
        result = []
        retrieval = OfficeRetrieval(
            drive=self.drive, regex=self.regex, no_subfolder=self.no_subfolder
        )
        files = retrieval.list_files_parallel(
            path=self.path, files=files, context=None, no_of_max_hits=10, workers=self.max_workers
        )
        if files:
            result.append("\nExample files: (max 10)\n")
            for file in files:
                props = file.properties
                result.append("\n" + "- " + props["name"])
            return "".join(result)
        result.append("\nNo files were found with the given instructions\n")
        return "".join(result)

    def create_drive(self) -> ClientObject:
        """Create drive"""
        s = self.client.sites.get_by_url(self.target_resource)
        return s.drive

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Execute workflow task"""
        _ = inputs

        context.report.update(
            ExecutionReport(entity_count=0, operation="wait", operation_desc="files listed.")
        )

        files: list[Any] = []
        entities = []
        retrieval = OfficeRetrieval(
            drive=self.drive, regex=self.regex, no_subfolder=self.no_subfolder
        )
        all_files = retrieval.list_files_parallel(
            path=self.path, files=files, context=context, workers=self.max_workers
        )
        for file in all_files:
            try:
                if context.workflow.status() == "Canceling":
                    break
            except AttributeError:
                pass
            props = file.properties
            entity_uri = props["webUrl"]
            values = [
                ["file"],
                [props["name"]],
                [props["webUrl"]],
                [props["parentReference"].name],
                [props["@microsoft.graph.downloadUrl"]],
                [str(props["createdBy"])],
                [props["createdDateTime"].strftime("%Y-%m-%d %H:%M:%S")],
                [props["eTag"]],
                [props["id"]],
                [str(props["lastModifiedBy"])],
                [props["lastModifiedDateTime"].strftime("%Y-%m-%d %H:%M:%S")],
                [props["cTag"]],
                [str(props["size"])],
            ]
            entities.append(Entity(uri=entity_uri, values=values))
            context.report.update(
                ExecutionReport(
                    entity_count=len(entities),
                    operation="write",
                    operation_desc="entities generated",
                )
            )

        context.report.update(
            ExecutionReport(
                entity_count=len(entities),
                operation="done",
                operation_desc="entities generated",
                sample_entities=Entities(entities=iter(entities[:10]), schema=generate_schema()),
            )
        )
        return Entities(entities=iter(entities), schema=generate_schema())
