from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from pathlib import Path
import importlib.metadata

from .base_config import BaseConfig, SettingsConfigDict, Field

# TODO: put this in a dedicated package and add it as dependency:
# from tgzr.package_manager import PackageManager
from tgzr.shell.package_manager import PackageManager

if TYPE_CHECKING:
    from .studio import Studio


class ProjectConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_project_defaults_")

    settings_provider: str | None = Field(
        None, description="Name of the settings plugin to use for this project"
    )


class Project:
    @classmethod
    def config_path(cls, studio: Studio, project_name: str) -> Path:
        return studio.projects_venv_path / project_name / ".tgzr_project"

    def __init__(self, studio: Studio, name: str) -> None:
        self._studio = studio
        self._name = name

        self._config_path = self.config_path(studio, name)
        self._config = ProjectConfig.from_file(self._config_path)

    @property
    def studio(self) -> Studio:
        return self._studio

    @property
    def config(self) -> ProjectConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._studio.projects_venv_path / self._name

    @property
    def venv_path(self) -> Path:
        return self._studio.project_venv_path(self.name)

    def save_config(self) -> Path:
        """Returns the path of the saved file."""
        self._config.to_file(
            self._config_path,
            allow_overwrite=True,
            header_text=f"tgzr {self.name!r} project config",
        )
        return self._config_path

    def exists(self) -> bool:
        return self.venv_path.exists()

    def ensure_exists(self):
        if not self.exists:
            self.create()

    def create(
        self,
        required_packages: list[str] = [],
        index: str | None = None,
        find_links: str | None = None,
        allow_prerelease: bool = False,
    ) -> None:
        """
        Create (or update) this Studio and seed it with the `tgzr.shell` package.
        If `index` is None, the workspace's default index is used.
        """
        self.studio.create_project(
            self.name,
            required_packages=required_packages,
            index=index,
            find_links=find_links,
            allow_prerelease=allow_prerelease,
        )

    def get_packages(self) -> list[tuple[str, str, str]]:
        """
        Return a list of (package_name, version) for every package
        installed in the project.
        """
        return self.studio.get_packages(self.name)

    def get_plugins(
        self, group_filter: str | None
    ) -> list[importlib.metadata.EntryPoint]:
        """
        Return a list of (plugin_group, plugin_name, plugin_entry_point) for every package
        installed in the project.
        """
        return self.studio.get_plugins(self.name, group_filter)

    def run_cmd(self, cmd_name: str, cmd_args: list[str]):
        """
        Run a command in this project's venv.
        Returns True if the command was executed successfuly (according to process return int).
        """
        return self.studio.run_cmd(cmd_name, cmd_args, self.name)

    def shell(
        self,
        shell_type: Literal["xonsh", "bash", "cmd", "powershell", "auto"],
        project_name: str | None = None,
    ):
        """
        Open a shell in this project's venv.
        Returns True if the command was executed successfuly (according to process return int).
        """
        return self.studio.shell(shell_type, self.name)
