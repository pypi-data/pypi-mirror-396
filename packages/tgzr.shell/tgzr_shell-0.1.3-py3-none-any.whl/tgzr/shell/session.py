from __future__ import annotations
from typing import Type

import os
from pathlib import Path

from .base_config import BaseConfig, Field, SettingsConfigDict
from .system import System
from .workspace import Workspace, WorkspaceConfig
from .studio import Studio, StudioConfig
from .project import Project

_DEFAULT_SESSION: Session | None = None


class SessionConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="tgzr_")
    verbose: bool = Field(False, description="Tchatty logs")


def set_default_session(session: Session):
    global _DEFAULT_SESSION
    _DEFAULT_SESSION = session
    # print("Default TGZR Session set.")
    env_home = os.environ.setdefault("tgzr_home", str(session.home))
    # print(f'  updated env "tgzr_home" to {env_home!r}')


def get_default_session() -> Session | None:
    """
    Return the session set as default with `set_default_session()`.
    If no session was set as default and the `tgzr_home` environment
    variable is set, a new session is created using it and set as
    default.
    Return None in other cases.
    """
    if _DEFAULT_SESSION is None:
        env_home = os.environ.get("tgzr_home") or os.environ.get("TGZR_HOME")
        if env_home is None:
            return None
        # print(f"Creating default TGZR session using 'tgzr_home' env var: {env_home}")
        session = Session(home=env_home)
        set_default_session(session)

    return _DEFAULT_SESSION


class Session:

    def __init__(self, home: Path | str | None = None):
        self._config_filename = ".tgzr"

        self._known_config_types: list[Type[BaseConfig]] = []
        self.declare_config_type(SessionConfig)
        self.declare_config_type(WorkspaceConfig)
        self.declare_config_type(StudioConfig)

        self._selected_studio_name: str | None = None
        self._selected_project_name: str | None = None

        self._system: System = System(self)
        self._workspace: Workspace | None = None

        if home is None:
            home = Path.cwd().resolve()
        else:
            home = Path(home)
        self.set_home(home)

    @property
    def home(self) -> Path:
        if self._home is None:
            raise ValueError("Home not set. Please use `set_home(path) first.`")
        return self._home

    def set_home(
        self, path: str | Path, ensure_config_found: bool = True
    ) -> Path | None:
        """Returns the path of the config loaded or None."""
        path = Path(path).resolve()
        config_path = SessionConfig.find_config_file(path, self._config_filename)
        if config_path is None:
            if ensure_config_found:
                raise FileNotFoundError(
                    f"Could not find a {self._config_filename} file under {path!r} and ancestors. "
                    "(Use `ensure_config_found=False` to bypass this error.)"
                )
            self._home = path
        else:
            self._home = config_path.parent
            self._config = SessionConfig.from_file(config_path)

        try:
            self._workspace = Workspace(self)
        except FileNotFoundError:
            self._workspace = None

        # If the given path is inside a studio, let's make this studio
        # the default one:
        if self._workspace and path.is_relative_to(self._workspace.path):
            studio_name = str(path)[len(str(self._workspace.path)) + 1 :].split(
                os.path.sep, 1
            )[0]
            try:
                self._workspace.set_default_studio(
                    studio_name,
                    ensure_exists=True,
                    save_config=False,  # Do not save, this is just for this session.
                )
            except FileNotFoundError:
                pass
        return config_path

    @property
    def system(self) -> System:
        return self._system

    @property
    def workspace(self) -> Workspace | None:
        return self._workspace

    @property
    def config(self) -> SessionConfig:
        if self._config is None:
            raise ValueError("Config not set. Please use `set_home(path) first.`")
        return self._config

    def save_config(self) -> Path:
        """Returns the path of the saved file."""
        return self.write_config_file(None, allow_overwrite=True)

    def write_config_file(
        self, path: str | Path | None, allow_overwrite: bool = False
    ) -> Path:
        """Returns the path of the saved file."""
        if path is None:
            path = self._home / self._config_filename
        path = Path(path).resolve()
        self._config.to_file(
            path,
            allow_overwrite=allow_overwrite,
            header_text="tgzr session config",
        )
        return path

    def declare_config_type(self, config_type: Type[BaseConfig]):
        """
        Declare the config type as used in the session.
        This is used for documentation and cli help.
        """
        self._known_config_types.append(config_type)

    def get_config_env_vars(self) -> list[tuple[str, list[tuple[str, str | None]]]]:
        """
        Returns a list of (name, description) for each config
        declared with `declare_config_type()`
        """
        config_env_vars = []
        for config_type in self._known_config_types:
            config_env_vars.append((config_type.__name__, config_type.used_env_vars()))
        return config_env_vars

    def set_verbose(self):
        self.config.verbose = True

    def set_quiet(self):
        self.config.verbose = False

    def select_studio(self, studio_name: str | None = None):
        self._selected_studio_name = studio_name

    @property
    def selected_studio_name(self) -> str | None:
        return self._selected_studio_name

    def get_selected_studio(self, ensure_exists: bool = True) -> Studio | None:
        if self.workspace is None:
            return None
        studio_name = self._selected_studio_name
        if studio_name is None:
            studio_name = self.workspace.default_studio_name()
        if studio_name is None:
            return None
        return self.workspace.get_studio(studio_name, ensure_exists)

    @property
    def selected_project_name(self) -> str | None:
        return self._selected_project_name

    def select_project(self, project_name: str | None = None):
        self._selected_project_name = project_name

    def get_selected_project(self) -> Project | None:
        if self.workspace is None:
            return None
        if self._selected_project_name is None:
            return None
        studio = self.get_selected_studio()
        if studio is None:
            return None
        return studio.get_project(self._selected_project_name)
