from types import ModuleType

import os
import subprocess

from ._base_app import _BaseShellApp


class ShellExeApp(_BaseShellApp):
    def __init__(
        self,
        exe_path: str,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: list[str] = [],
    ):
        super().__init__(app_name, run_module, app_id, app_groups)
        self._exe_path = exe_path

    def exe_path(self) -> str:
        return self._exe_path

    def run_app(self):
        # TODO: find out how we can pass tgzr.cli args to here:
        os.system(self.exe_path())


class ShellHostApp(ShellExeApp):
    """
    This special type of application
    represents an "Integrated DCC".
    i.e: a DCC which can be controled
    by TGZR.
    """

    # TODO: implement this in a dedicated package.

    def __init__(
        self,
        host_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: list[str] = [],
    ):
        super().__init__(None, host_name, run_module, app_id, app_groups)

    def env(self) -> dict[str, str]:
        """
        Subclass will typically reimplement this to
        return the appropriate env dict.
        """
        return {}

    def exe_path(self) -> str:
        """
        Subclass will typically implement this to
        locate the appropriate exe path and return it.
        """
        raise NotImplementedError()

    def cmd(self) -> list[str]:
        """
        Subclass will typically reimplement this to
        build the full command, using self.exe_path().
        """
        return [self.exe_path()]

    def run_app(self):

        # TODO: implement a subprocess manager to keep track
        # of all popen.
        popen = subprocess.Popen(self.cmd(), env=self.env())
