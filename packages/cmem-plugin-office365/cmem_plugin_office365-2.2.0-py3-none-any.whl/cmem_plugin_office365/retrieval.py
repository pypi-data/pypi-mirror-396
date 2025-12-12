"""Parallel directory retrieval"""

import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from office365.runtime.client_object import ClientObject


def context_report(context: ExecutionContext, files: list[Any]) -> None:
    """Report for user context"""
    if context is not None:
        context.report.update(
            ExecutionReport(
                entity_count=len(files), operation="wait", operation_desc="files listed"
            )
        )


def _strip_path(path: str) -> str:
    """Strip path of trailing '/'"""
    if path[-1] == "/":
        path = path[:-1]
    return path


class OfficeRetrieval:
    """Retrieval class for Office 365 folders and files"""

    def __init__(self, drive: ClientObject, no_subfolder: bool, regex: str) -> None:
        self.drive = drive
        self.no_subfolder = no_subfolder
        self.regex = regex
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def list_files_parallel(  # noqa: PLR0913
        self,
        path: str,
        files: list[Any],
        context: ExecutionContext | None,
        depth: int = -1,
        curr_depth: int = 0,
        no_of_max_hits: int = -1,
        workers: int = 32,
    ) -> list[Any]:
        """List files"""
        if curr_depth == 0:
            self.stop_event.clear()
        self.cancel_listdir(context)
        if self.stop_event.is_set() or (depth != -1 and curr_depth >= depth):
            return files

        subdirectories: list[str] = []
        items = self._get_folder_items(path)

        for item in items:
            self.cancel_listdir(context)
            if self.stop_event.is_set():
                return files

            added = self.add_node(files, item, no_of_max_hits)
            context_report(context, files)

            if added and self.check_stop(files, no_of_max_hits):
                return files

            if item.is_folder and not self.no_subfolder:
                subdirectories.append(path + "/" + item.name)

        if not self.stop_event.is_set() and subdirectories:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(
                        self.list_files_parallel,
                        sd,
                        files,
                        None,
                        depth,
                        curr_depth + 1,
                        no_of_max_hits,
                        workers,
                    )
                    for sd in subdirectories
                ]
                for fut in as_completed(futures):
                    self.cancel_listdir(context)
                    if self.stop_event.is_set():
                        break
                    fut.result()
                    context_report(context, files)

        context_report(context, files)
        return files

    def cancel_listdir(self, context: ExecutionContext) -> None:
        """Cancel listdir if workflow is cancelled"""
        try:
            if context.workflow.status() == "Canceling":
                self.stop_event.set()
        except AttributeError:
            pass

    def add_node(self, files: list[Any], item: Any, no_of_max_hits: int) -> bool:  # noqa: ANN401
        """Add file or folder node to result"""
        with self.lock:
            if no_of_max_hits != -1 and len(files) >= no_of_max_hits:
                self.stop_event.set()
                return False

            props = item.properties
            if (re.fullmatch(self.regex, props["name"])) and not item.is_folder:
                files.append(item)
                if no_of_max_hits != -1 and len(files) >= no_of_max_hits:
                    self.stop_event.set()
                return True

        return False

    def check_stop(self, files: list[Any], max_results: int) -> bool:
        """Check whether max_results reached and stop if so"""
        with self.lock:
            if max_results != -1 and len(files) >= max_results:
                self.stop_event.set()
                return True
        return False

    def _get_folder_items(self, path: str) -> Any:  # noqa: ANN401
        """Get the items within a folder"""
        if path == "":
            return self.drive.root.children.get().execute_query()
        path = _strip_path(path)
        return self.drive.root.get_by_path(path).children.get().execute_query()
