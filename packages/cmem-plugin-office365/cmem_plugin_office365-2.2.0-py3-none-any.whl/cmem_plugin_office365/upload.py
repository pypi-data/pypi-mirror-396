"""Upload workflow task for Office 365"""

import gzip
import io
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import Path

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import Entities
from cmem_plugin_base.dataintegration.parameter.choice import ChoiceParameterType
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import (
    File,
    FileEntitySchema,
)
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access
from office365.graph_client import GraphClient
from office365.runtime.client_object import ClientObject

from cmem_plugin_office365.autocompletion import (
    DriveDirectoryParameterType,
    FolderDirectoryParameterType,
    ResourceDirectoryParameterType,
)

RESOURCE_CHOICE = OrderedDict({"personal": "Personal", "site": "Site"})
MAX_WORKERS = 32


def _is_gzip(stream: io.BufferedReader) -> bool:
    head = stream.read(2)
    stream.seek(0)
    return head == b"\x1f\x8b"


@Plugin(
    label="Office 365 Upload Files",
    plugin_id="cmem_plugin_office365-Upload",
    description="Upload files to OneDrive or a site Sharepoint",
    documentation="""
This workflow task upload files to specified Office 365 instance.
For this to work a registered app in Microsoft's Entra ID space is necessary.
Further information can be found [here](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).

After registering an application, it needs to be granted application wide API permissions:

- Files.Read.All, Files.Write.All
- Sites.Read.All, Sites.Write.All

Admin consent is required to activate these permissions.
With this setup, anyone with the secret can access all users' OneDrives and all Sharepoint/Team
sites.

#### Important

Make sure only trusted admins can create or manage secrets!
Whoever holds the secrets has all the access to granted resources so best not to distribute
recklessly.
    """,
    icon=Icon(package=__package__, file_name="o365-upload.svg"),
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
class UploadPlugin(WorkflowPlugin):
    """Upload plugin Office 365"""

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
        self.max_workers = setup_max_workers(max_workers)
        self.client = GraphClient(tenant=tenant_id).with_client_secret(
            self.client_id, self.client_secret
        )
        self.drive = self.create_drive()
        self._set_ports()

    def _set_ports(self) -> None:
        """Define input/output ports based on the configuration"""
        self.input_ports = FixedNumberOfInputs([FixedSchemaPort(schema=FileEntitySchema())])
        self.output_port = None

    def create_drive(self) -> ClientObject:
        """Create drive"""
        s = self.client.sites.get_by_url(self.target_resource)
        return s.drive

    def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities:
        """Execute the workflow task"""
        if len(inputs) == 0:
            raise ValueError("No input was given!")

        schema = FileEntitySchema()
        setup_cmempy_user_access(context.user)

        files = self.upload_with_input(context, inputs)

        entities = [schema.to_entity(file) for file in files]

        context.report.update(
            ExecutionReport(
                entity_count=len(entities),
                operation="write",
                operation_desc="files uploaded",
                sample_entities=Entities(entities=iter(entities[:10]), schema=schema),
            )
        )

        return Entities(entities=iter(entities), schema=schema)

    def upload_with_input(
        self, context: ExecutionContext, inputs: Sequence[Entities]
    ) -> list[File]:
        """Upload of files from a given input"""
        files: list[File] = []
        schema = FileEntitySchema()
        for entity in inputs[0].entities:
            try:
                if context.workflow.status() == "Canceling":
                    break
            except AttributeError:
                pass

            file = schema.from_entity(entity)
            file_name = Path(file.path).name

            context.report.update(
                ExecutionReport(
                    entity_count=len(files),
                    operation="upload",
                    operation_desc=f"uploading {file_name}",
                )
            )

            with file.read_stream(context.task.project_id()) as input_file:
                # Wrap input in buffered stream if needed
                buffered = io.BufferedReader(input_file)

                # Check if Gzip by peeking at first two bytes
                if _is_gzip(buffered):
                    decompressed_stream = gzip.GzipFile(fileobj=buffered)
                else:
                    decompressed_stream = buffered  # type: ignore[assignment]

                # Decide whether it's text or binary (peek and try decode)
                sample = decompressed_stream.read(1024)
                decompressed_stream.seek(0)

                try:
                    sample.decode("utf-8")
                    is_text = True
                except UnicodeDecodeError:
                    is_text = False

                if is_text:
                    stream_for_upload = io.TextIOWrapper(decompressed_stream, encoding="utf-8")
                else:
                    stream_for_upload = decompressed_stream  # type: ignore[assignment]

                if self.path == "":
                    self.drive.root.upload(file_name, stream_for_upload).execute_query()
                else:
                    self.path = _strip_path(self.path)
                    self.drive.root.get_by_path(self.path).upload(
                        file_name, stream_for_upload
                    ).execute_query()

            files.append(
                File(
                    path=file.path,
                    entry_path=file.entry_path,
                    mime=file.mime,
                    file_type=file.file_type,
                )
            )
        return files


def setup_max_workers(max_workers: int) -> int:
    """Return the correct number of workers"""
    if 0 < max_workers <= MAX_WORKERS:
        return max_workers
    raise ValueError("Range of max_workers exceeded")


def _strip_path(path: str) -> str:
    """Strip path of trailing '/'"""
    if path[-1] == "/":
        path = path[:-1]
    return path
