"""Office 365 download workflow task plugin"""

import tempfile
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile
from office365.graph_client import GraphClient
from office365.runtime.client_object import ClientObject

from cmem_plugin_office365.autocompletion import (
    DriveDirectoryParameterType,
    FolderDirectoryParameterType,
    ResourceDirectoryParameterType,
)
from cmem_plugin_office365.list import generate_schema
from cmem_plugin_office365.retrieval import OfficeRetrieval

RESOURCE_CHOICE = OrderedDict({"personal": "Personal", "site": "Site"})
MAX_WORKERS = 32


def setup_max_workers(max_workers: int) -> int:
    """Return the correct number of workers"""
    if 0 < max_workers <= MAX_WORKERS:
        return max_workers
    raise ValueError("Range of max_workers exceeded")


@Plugin(
    label="Download Office 365 Files",
    plugin_id="cmem_plugin_office365-Download",
    description="Download files from Microsoft OneDrive or Sites",
    documentation="""
This workflow task downloads files from a specified Office 365 instance.
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
    icon=Icon(package=__package__, file_name="o365-download.svg"),
    actions=[
        PluginAction(
            name="preview_results",
            label="Preview results",
            description="Preview the results (max. 10).",
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
class DownloadPlugin(WorkflowPlugin):
    """Download Plugin Office 365"""

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
        self.download_dir = tempfile.mkdtemp()
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
        self.input_ports = FixedNumberOfInputs([FixedSchemaPort(schema=generate_schema())])
        self.output_port = FixedSchemaPort(schema=FileEntitySchema())

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
            result.append("\nExample files: (max. 10)\n")
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
        """Execute the workflow task to download files from Office 365"""
        _ = context
        _ = inputs
        entities = []
        schema = FileEntitySchema()

        if len(inputs) == 0:
            files = self.download_files_no_input(context)
            try:
                if context.workflow.status() == "Canceling":
                    return Entities(entities=iter([]), schema=schema)
            except AttributeError:
                pass
            entities = [schema.to_entity(file) for file in files]
            context.report.update(
                ExecutionReport(
                    entity_count=len(entities),
                    operation="write",
                    operation_desc="files downloaded",
                    sample_entities=Entities(entities=iter(entities[:10]), schema=schema),
                )
            )
            return Entities(entities=iter(entities), schema=schema)

        files = self.download_files_input(inputs, context)
        entities = [schema.to_entity(file) for file in files]
        context.report.update(
            ExecutionReport(
                entity_count=len(entities),
                operation="done",
                operation_desc="files downloaded",
                sample_entities=Entities(entities=iter(entities[:10]), schema=schema),
            )
        )
        return Entities(entities=iter(entities), schema=schema)

    def download_files_no_input(self, context: ExecutionContext) -> list:
        """Download files if no input is given"""
        retrieval = OfficeRetrieval(
            drive=self.drive,
            no_subfolder=self.no_subfolder,
            regex=self.regex,
        )
        office_files = retrieval.list_files_parallel(path=self.path, files=[], context=context)
        entity_files = []
        for file in office_files:
            local_path = self.download_dir / Path(file.name)
            with local_path.open("wb") as f:
                file.download(f).execute_query()
            entity_files.append(LocalFile(str(local_path)))
        return entity_files

    def download_files_input(self, inputs: Sequence[Entities], context: ExecutionContext) -> list:
        """Download files if an input is given"""
        entity_files = []
        for entity in inputs[0].entities:
            try:
                if context.workflow.status() == "Canceling":
                    break
            except AttributeError:
                pass

            file_item = (
                self.client.shares.by_url(entity.values[2][0]).drive_item.get().execute_query()
            )
            local_path = self.download_dir / Path(entity.values[1][0])
            with local_path.open("wb") as f:
                file_item.download(f).execute_query()
            entity_files.append(LocalFile(str(local_path)))
        return entity_files
