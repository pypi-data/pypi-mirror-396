from __future__ import annotations
from typing import TYPE_CHECKING, Literal

import os
from pathlib import Path
import platform
import tempfile
import importlib.metadata

from .base_config import BaseConfig, SettingsConfigDict, Field
from .project import Project

# TODO: put this in a dedicated package and add it as dependency:
# from tgzr.package_manager import PackageManager
from tgzr.shell.package_manager import PackageManager, Venv

if TYPE_CHECKING:
    from .workspace import Workspace


class StudioConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_studio_defaults_")

    default_index: str | None = Field(
        None,
        description="Default package index for this studio. Use None to fallback to Work config",
    )


class Studio:

    @classmethod
    def config_path(cls, workspace: Workspace, name: str) -> Path:
        return workspace.path / name / ".tgzr_studio"

    def __init__(self, workspace: Workspace, name: str) -> None:
        self._workspace = workspace
        self._name = name
        self._config_path = self.config_path(workspace, name)
        self._config = StudioConfig.from_file(self._config_path)

        self._venvs_path = self.path / "venvs"
        self._tgzr_venv_group = "_"
        self._tgzr_venv_name = "tgzr"
        self._projects_venv_group = "projects"

    @property
    def config(self) -> StudioConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    @property
    def path(self) -> Path:
        return self.workspace.path / self.name

    def resolve_index(self, index: str | None) -> str | None:
        """
        Returns the path of an index, making it absolute in case
        of relative local path.

        If index is None, the default index will be returned.
        If no default index in found on the Studio nor on the Workspace,
        None is returned.
        """
        index = index or self.config.default_index
        return self._workspace.resolve_index(index, relative_to=self.path)

    def save_config(self) -> Path:
        """Returns the path of the saved file."""
        self._config.to_file(
            self._config_path,
            allow_overwrite=True,
            header_text="tgzr studio config",
        )
        return self._config_path

    def exists(self) -> bool:
        return self.path.exists()

    def ensure_exists(self):
        if not self.exists:
            self.create()

    @property
    def projects_venv_path(self) -> Path:
        return self._venvs_path / self._projects_venv_group

    def project_venv_path(self, project_name: str) -> Path:
        return self.projects_venv_path / project_name

    def get_project_names(self) -> list[str]:
        # TODO: filter by looking for the project config file
        if not self.projects_venv_path.is_dir():
            return []
        return os.listdir(self.projects_venv_path)

    def get_project(self, project_name: str) -> Project:
        return Project(self, project_name)

    def create(
        self,
        index: str | None = None,
        find_links: str | None = None,
        allow_prerelease: bool = False,
    ):
        """
        Create (or update) this Studio and seed it with the `tgzr.shell` package.
        If `index` is None, the studio's default index is used.
        """
        self.path.mkdir(exist_ok=True)
        self.save_config()

        pm = PackageManager(self._venvs_path)
        venv = pm.create_venv(
            self._tgzr_venv_name,
            group=self._tgzr_venv_group,
            exist_ok=True,
            prompt=self.name,
        )

        index = self.resolve_index(index)
        ok = venv.install_packages(
            "tgzr.shell tgzr.shell_apps.manager_panel",
            index=index,
            find_links=find_links,
            allow_prerelease=allow_prerelease,
            update=True,
        )
        if not ok:
            raise Exception("Could not install tgzr in Studio :( Aborting.")

        tgzr_exe = venv.get_exe("tgzr")
        tgzr_shortcut = self.path / "tgzr"
        if tgzr_shortcut.exists():
            tgzr_shortcut.unlink()
        pm.create_shortcut(tgzr_exe, tgzr_shortcut, relative=True)

    def create_project(
        self,
        project_name: str,
        required_packages: list[str] = [],
        index: str | None = None,
        find_links: str | None = None,
        allow_prerelease: bool = False,
    ) -> tuple[bool, list[str]]:
        """
        Create (or update) this project and seed it with the `tgzr.shell` package.
        If `index` is None, the studio's default index is used.
        All requirements in `required_packages` are installed two.

        Returns (all_requirement_install_ok, list_of_failed_install)

        """
        self.path.mkdir(exist_ok=True)
        self.save_config()

        pm = PackageManager(self._venvs_path)
        venv = pm.create_venv(
            project_name,
            group=self._projects_venv_group,
            exist_ok=True,
            prompt=f"{self.name}:{project_name}",
        )

        index = self.resolve_index(index)
        ok = venv.install_packages(
            "tgzr.shell tgzr.shell_apps.manager_panel",
            index=index,
            find_links=find_links,
            allow_prerelease=allow_prerelease,
            update=True,
        )
        if not ok:
            raise Exception("Could not install tgzr in Studio :( Aborting.")

        tgzr_exe = venv.get_exe("tgzr")
        tgzr_shortcut = self.path / f"tgzr_{project_name}"
        if tgzr_shortcut.exists():
            tgzr_shortcut.unlink()
        pm.create_shortcut(tgzr_exe, tgzr_shortcut, relative=True)

        install_errors = []
        all_ok = True
        for required_package in required_packages:
            print(f"--- Installing required package(s): {required_package}")
            ok = venv.install_packages(
                required_package,
                index=index,
                find_links=find_links,
                allow_prerelease=allow_prerelease,
                update=True,
            )
            if not ok:
                all_ok = False
                install_errors.append(required_package)
                print(
                    f"WARNING: Could not install {required_package!r} in Project {self.name!r} :("
                )
            else:
                print(f"Package(s) {required_package!r} installed successfully.")

        return all_ok, install_errors

    def get_venv(self, project_name: str | None) -> Venv:
        """
        Return the package_manager.Venv for the given project.
        If project_name is not provided, the studio venv is used ('_/tgzr')
        """
        if project_name is None:
            group = self._tgzr_venv_group
            venv_name = self._tgzr_venv_name
        else:
            group = self._projects_venv_group
            venv_name = project_name
        pm = PackageManager(self._venvs_path)
        venv = pm.get_venv(venv_name, group)
        return venv

    def get_cmd_output(
        self, cmd_name: str, cmd_args: list[str], project_name: str | None = None
    ) -> tuple[str, str]:
        """
        Run a command in the venv for the given project and returns the stdout and stderr.
        If project_name is not provided, the studio venv is used ('_/tgzr')
        """
        venv = self.get_venv(project_name)
        return venv.get_cmd_output(cmd_name, cmd_args)

    def run_cmd(
        self, cmd_name: str, cmd_args: list[str], project_name: str | None = None
    ):
        """
        Run a command in the venv for the given project.
        If project_name is not provided, the studio venv is used ('_/tgzr')

        Returns True if the command was executed successfuly (according to process return int).
        """
        venv = self.get_venv(project_name)
        return venv.run_cmd(cmd_name, cmd_args)

    def get_packages(
        self, project_name: str | None = None
    ) -> list[tuple[str, str, str]]:
        """
        Return a list of (package_name, version, editable_path) for packages installed
        in the specified project.
        If project_name is not provided, the "master" venv is used ('_/tgzr')
        """
        venv = self.get_venv(project_name)
        return venv.get_packages()

    def get_plugins(
        self, project_name: str | None, group_filter: str | None
    ) -> list[importlib.metadata.EntryPoint]:
        venv = self.get_venv(project_name)
        return venv.get_plugins(group_filter)

    def shell(
        self,
        shell_type: Literal["xonsh", "bash", "cmd", "powershell", "auto"],
        project_name: str | None = None,
    ):
        """
        Open a shell in the venv for the given project.
        If project_name is not provided, the "master" venv is used ('_/tgzr')

        Returns True if the command was executed successfuly (according to process return int).
        """
        if project_name is None:
            group = self._tgzr_venv_group
            venv_name = self._tgzr_venv_name
        else:
            group = self._projects_venv_group
            venv_name = project_name

        pm = PackageManager(self._venvs_path)
        venv = pm.get_venv(venv_name, group)

        if shell_type == "auto":
            if platform.system() == "Windows":
                shell_type = "cmd"
            else:
                shell_type = "bash"

        if shell_type == "bash":
            activate = str(venv.get_exe("activate"))
            script = f"source /home/dee/.bashrc; source {activate}"
            try:
                fp, script_path = tempfile.mkstemp(prefix="tgzr_studio_shell_init_file")
                os.write(fp, script.encode())
            finally:
                os.close(fp)
            cmd = f"bash --init-file {script_path}"

        elif shell_type == "xonsh":
            xonsh = venv.get_exe("xonsh")
            if not xonsh.exists():
                venv.install_packages("xonsh[full]")
            cmd = f"{xonsh}"
        else:  # all windows shell types:
            activate = str(venv.get_exe("activate")).replace("/", "\\")
            cmd = f"start cmd /k {activate}"

        return venv.execute_cmd(cmd)
