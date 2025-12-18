from typing import cast

from types import ModuleType
from ._base_app import _BaseShellApp


class ShellQtpyApp(_BaseShellApp):
    def __init__(
        self,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: list[str] = [],
    ):
        super().__init__(app_name, run_module, app_id, app_groups)

    def run_app(self, main_widget: object):
        # NOTE:
        # The nice gui app must be runnable with:
        # `python -m <self.run_native_module>`

        # Do the import here instead of global to have the module
        # loadable even without the [nicegui] extra requirements.
        # (I know...)
        from qtpy.QtWidgets import QWidget

        widget = cast(QWidget, main_widget)
        raise NotImplementedError()
        # TODO: implement this:
        # Add a 'qtpy' extra requirement with qtpy
        # Build a QApplication here, instantiate self.main_widget
        # Run the app.
