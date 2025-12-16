import os
from typing import TYPE_CHECKING

import httpx

from .client import _Client

if TYPE_CHECKING:
    from spiral.core.authn import Authn

    from .admin import AdminService
    from .filesystems import FileSystemsService
    from .key_space_indexes import KeySpaceIndexesService
    from .organizations import OrganizationsService
    from .projects import ProjectsService
    from .telemetry import TelemetryService
    from .text_indexes import TextIndexesService
    from .workloads import WorkloadsService


class SpiralAPI:
    def __init__(self, base_url: str, authn: "Authn"):
        self.base_url = base_url
        self.client = _Client(
            httpx.Client(
                base_url=self.base_url,
                timeout=None if "PYTEST_VERSION" in os.environ else 60,
            ),
            authn,
        )

    @property
    def _admin(self) -> "AdminService":
        from .admin import AdminService

        return AdminService(self.client)

    @property
    def organizations(self) -> "OrganizationsService":
        from .organizations import OrganizationsService

        return OrganizationsService(self.client)

    @property
    def projects(self) -> "ProjectsService":
        from .projects import ProjectsService

        return ProjectsService(self.client)

    @property
    def file_systems(self) -> "FileSystemsService":
        from .filesystems import FileSystemsService

        return FileSystemsService(self.client)

    @property
    def workloads(self) -> "WorkloadsService":
        from .workloads import WorkloadsService

        return WorkloadsService(self.client)

    @property
    def text_indexes(self) -> "TextIndexesService":
        from .text_indexes import TextIndexesService

        return TextIndexesService(self.client)

    @property
    def key_space_indexes(self) -> "KeySpaceIndexesService":
        from .key_space_indexes import KeySpaceIndexesService

        return KeySpaceIndexesService(self.client)

    @property
    def telemetry(self) -> "TelemetryService":
        from .telemetry import TelemetryService

        return TelemetryService(self.client)
