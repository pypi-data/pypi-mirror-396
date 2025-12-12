"""Autocompletion"""

from typing import Any, ClassVar

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from office365.graph_client import GraphClient
from office365.runtime.client_object import ClientObject


def list_all_sites(depend_on_parameter_values: list[Any]) -> ClientObject:
    """List all available sites"""
    client = get_office_client(depend_on_parameter_values)
    return client.sites.get().execute_query()


def get_office_client(depend_on_parameter_values: list[Any]) -> GraphClient:
    """Initialize the office client"""
    return GraphClient(tenant=depend_on_parameter_values[0]).with_client_secret(
        client_id=depend_on_parameter_values[1],
        client_secret=depend_on_parameter_values[2]
        if isinstance(depend_on_parameter_values[2], str)
        else depend_on_parameter_values[2].decrypt(),
    )


def sort_suggestions(suggestions: list[Autocompletion], query_terms: list[str]) -> None:
    """Sort autocompleted suggestions"""
    suggestions.sort(
        key=lambda x: (
            not all(term.lower() in x.label.lower() for term in query_terms),
            x.label.lower(),
        )
    )


class ResourceDirectoryParameterType(StringParameterType):
    """Resource autocompletion parameter"""

    def __init__(
        self,
        url_expand: str,
        display_name: str,
    ) -> None:
        self.url_expand = url_expand
        self.display_name = display_name
        self.suggestions: list[Autocompletion] = []

    allow_only_autocompleted_values = True

    autocompletion_depends_on_parameters: ClassVar[list[str]] = [
        "tenant_id",
        "client_id",
        "client_secret",
        "type_resource",
    ]

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocomplete resources"""
        _ = context
        entered_term = "".join(query_terms).lower()
        target_type = depend_on_parameter_values[3]
        all_sites = list_all_sites(depend_on_parameter_values)
        autocompletion = []

        for site in all_sites:
            props = site.properties
            if (
                not props["isPersonalSite"]
                and target_type == "site"
                and entered_term in props["webUrl"].lower()
            ):
                autocompletion.append(Autocompletion(value=props["webUrl"], label=props["webUrl"]))
            elif (
                props["isPersonalSite"]
                and target_type == "personal"
                and entered_term in props["webUrl"].lower()
            ):
                url = props["webUrl"]
                label = props["webUrl"]
                autocompletion.append(Autocompletion(value=url, label=label))
        sort_suggestions(autocompletion, query_terms)
        self.suggestions = autocompletion
        return self.suggestions


def add_parent_folder(result: list[Autocompletion], selected_path: str) -> None:
    """Add parent folder of given path to autocompletion list"""
    parent_folder = "/".join(selected_path.rstrip("/").split("/")[:-1])
    if parent_folder:
        parent_folder = f"{parent_folder}/"
        result.append(Autocompletion(value=parent_folder, label=parent_folder))


def _get_parent_folder(path: str) -> str:
    paths = path.split("/")
    return "/".join(paths[:-1])


class FolderDirectoryParameterType(StringParameterType):
    """Folder autocompletion parameter"""

    def __init__(
        self,
        url_expand: str,
        display_name: str,
    ) -> None:
        self.url_expand = url_expand
        self.display_name = display_name
        self.suggestions: list[Autocompletion] = []

    autocompletion_depends_on_parameters: ClassVar[list[str]] = [
        "tenant_id",
        "client_id",
        "client_secret",
        "target_resource",
        "drives",
    ]

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocompletion for folder"""
        _ = context

        entered_directory = " ".join(query_terms)
        parent_folder = _get_parent_folder(entered_directory)
        result: list[Autocompletion] = []
        client = get_office_client(depend_on_parameter_values)
        drive = client.drives[depend_on_parameter_values[4]].get().execute_query()
        if parent_folder == "":
            drive_items = drive.root.children.get().execute_query()
            for item in drive_items:
                props = item.properties
                if "folder" in props:
                    result.append(
                        Autocompletion(value=props["name"] + "/", label=props["name"] + "/")
                    )
        else:
            drive_items = drive.root.get_by_path(parent_folder).children.get().execute_query()
            for item in drive_items:
                props = item.properties
                if "folder" in props:
                    result.append(
                        Autocompletion(
                            value=f"{parent_folder}/{props['name']}",
                            label=f"{parent_folder}/{props['name']}",
                        )
                    )
            result.append(
                Autocompletion(
                    value=f"{parent_folder}",
                    label=f"{parent_folder}",
                )
            )
        return result


class DriveDirectoryParameterType(StringParameterType):
    """Drive autocompletion parameter"""

    autocomplete_value_with_labels = True
    autocompletion_depends_on_parameters: ClassVar[list[str]] = [
        "tenant_id",
        "client_id",
        "client_secret",
        "target_resource",
    ]

    def __init__(
        self,
        url_expand: str,
        display_name: str,
    ) -> None:
        self.url_expand = url_expand
        self.display_name = display_name
        self.suggestions: list[Autocompletion] = []

    def label(
        self, value: str, depend_on_parameter_values: list[Any], context: PluginContext
    ) -> str | None:
        """Get label"""
        _ = context
        client = get_office_client(depend_on_parameter_values)
        target = depend_on_parameter_values[3]
        drives = client.sites.get_by_url(target).drives.get().execute_query()
        for drive in drives:
            if drive.id == value:
                return str(drive.name)
        return None

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Autocomplete the drives"""
        _ = query_terms
        _ = context
        client = get_office_client(depend_on_parameter_values)
        target = depend_on_parameter_values[3]
        drives = client.sites.get_by_url(target).drives.get().execute_query()
        return [Autocompletion(value=drive.id, label=drive.name) for drive in drives]
