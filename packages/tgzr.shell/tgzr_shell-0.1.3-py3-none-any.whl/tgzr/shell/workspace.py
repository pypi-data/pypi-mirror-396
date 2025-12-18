from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from pathlib import Path
import platform

from .base_config import BaseConfig, SettingsConfigDict, Field

# TODO: put this in a dedicated package and add it as dependency:
# from tgzr.package_manager import PackageManager
from tgzr.shell.package_manager import PackageManager

from .studio import Studio

if TYPE_CHECKING:
    from .session import Session


class WorkspaceConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_workspace_")

    default_studio_name: str | None = Field(
        None, description="Name of the default studio"
    )
    default_index: str | None = Field(
        None,
        description="Default package index for all studios. Use None for https://pypi.org/simple",
    )


class Workspace:
    def __init__(self, session: Session):
        if not session._home.is_dir():
            raise FileNotFoundError(
                f'The path "{self._path}" is not a directory, cannot use it as Workspace parent.'
            )
        self._path = (session.home / "Workspace").resolve()
        if not self._path.exists():
            self._path.mkdir()
        self._config_path = self._path / ".tgzr_workspace"
        self._config = WorkspaceConfig.from_file(self._config_path)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def config(self) -> WorkspaceConfig:
        return self._config

    def studio_names(self) -> list[str]:
        """
        Return the names of the installed studios.
        """
        if not self._path.exists():
            return []
        names = []
        for path in self._path.iterdir():
            config_path = Studio.config_path(self, path.name)
            if config_path.exists():
                names.append(path.name)
        return sorted(names)

    def get_studios(self) -> list[Studio]:
        return [
            self.get_studio(name, ensure_exists=False) for name in self.studio_names()
        ]

    def set_default_studio(
        self,
        studio_name: str | None,
        ensure_exists: bool = True,
        save_config: bool = True,
    ) -> None:
        if studio_name is None:
            self._config.default_studio_name = None
        else:
            if ensure_exists:
                # will raise if studio does not exists on disk:
                self.get_studio(studio_name, ensure_exists=True)
            self._config.default_studio_name = studio_name
        if save_config:
            self.save_config()

    def save_config(self) -> Path:
        """Returns the path of the saved file."""
        self._config.to_file(
            self._config_path,
            allow_overwrite=True,
            header_text="tgzr workspace config",
        )
        return self._config_path

    def default_studio_name(self) -> str | None:
        """The name of the default studio, or None"""
        return self.config.default_studio_name

    def get_default_studio(self, ensure_exists: bool = True) -> Studio | None:
        name = self._config.default_studio_name
        if name is None:
            return None
        return self.get_studio(name, ensure_exists)

    def get_studio(self, name: str, ensure_exists: bool = True) -> Studio:
        studio = Studio(self, name)
        if ensure_exists and not studio.exists():
            raise FileNotFoundError
        return studio

    def resolve_index(
        self, index: str | None, relative_to: Path | None = None
    ) -> str | None:
        """
        Returns the path of an index, making it absolute in case
        of relative local path.
        If `relative_to` is not provided, `self.path` is used.

        If index is None, the default index will be returned.
        If no default index is set, None is returned.
        """
        index = index or self.config.default_index
        if index is None:
            return None
        if not "://" in index:
            local_index = Path(index)
            if not local_index.is_absolute():
                relative_to = relative_to or self.path
                index = str((relative_to / local_index).resolve())
        return index
