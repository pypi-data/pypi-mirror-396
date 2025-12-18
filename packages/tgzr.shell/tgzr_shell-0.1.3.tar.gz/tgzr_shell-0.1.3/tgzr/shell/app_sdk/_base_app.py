from __future__ import annotations
from types import ModuleType

from pathlib import Path
import inspect

import click

from tgzr.cli.utils import TGZRCliGroup

from .exceptions import MissingRunNativeModule


class _BaseShellApp:

    def __init__(
        self,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: list[str] = [],
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_module`:
            The python module used to run the app.
            Must be a valid modules with appropriate safeguards.
            NOTE: using None will raise an exception showing you
            how to implement this module.

        """
        frame: inspect.FrameInfo = inspect.stack()[1]
        if app_name is None:
            app_name = frame.function
            # print("---> AUTO APP NAME:", repr(app_name))

        if app_id is None:
            module = inspect.getmodule(frame[0])
            app_id = module and module.__name__ or "???"
            # print("---> AUTO APP ID:", app_id)

        if run_module is None:
            raise MissingRunNativeModule(self)
        self.run_native_module = run_module

        self.app_name = app_name
        self.app_id = app_id
        self.app_groups = app_groups

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        """
        Called when tgzr.shell.cli_plugin.app_cli has created and
        registered a cli command to execute this app.

        Subclasses can override this to alter the cmd or set it as default
        on the root group.

        Default does nothing.
        """
        pass

    def run_app(self):
        raise NotImplementedError()
