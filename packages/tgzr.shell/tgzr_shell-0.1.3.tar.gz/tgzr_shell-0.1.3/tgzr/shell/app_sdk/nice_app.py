from types import ModuleType

import inspect
from pathlib import Path

from ._base_app import _BaseShellApp
from .exceptions import MissingRunDevModule


class ShellNiceApp(_BaseShellApp):

    def __init__(
        self,
        app_name: str,
        run_native_module: ModuleType | None,
        run_dev_module: ModuleType | None,
        reload_root_path: Path | None = None,
        static_file_path: Path | None = None,
        app_id: str | None = None,
        app_groups: list[str] = [],
        dark: bool = True,
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_native_module` and `run_dev_module`:
            The python modules used to run the app in native or dev mode.
            Must be modules with appropriate safeguards.
            NOTE: using None in either of these values will raise an exception showing you
            how to implement these modules.

        `reload_root_path`:
            Path under which a file modification will trigger an app reload.
            Default value is two parent up from the caller's file.

        `static_file_path`:
            Must be an existing Path if the app needs to use static images and/or movies
            files.
            NOTE: this Path must contain two folders: `assets` and `medias`.

        `dark`:
            Force the app be be in dark mode.
        """
        super().__init__(
            app_name, run_module=run_native_module, app_id=app_id, app_groups=app_groups
        )

        if reload_root_path is None:
            frame: inspect.FrameInfo = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            reload_root_path = Path(module.__file__).parent
        self.reload_root_path = reload_root_path

        if run_dev_module is None:
            raise MissingRunDevModule(self)
        self.run_dev_module = run_dev_module

        self.dark = dark

        self.assets_path = None
        self.medias_path = None
        if static_file_path is not None:
            self.assets_path = static_file_path / "assets"
            if not self.assets_path.is_dir():
                # TODO: decide if we should warn or raise:
                print(ValueError(f"The path {self.assets_path} is not a folder :/"))
            self.medias_path = static_file_path / "medias"
            if not self.medias_path.is_dir():
                # TODO: decide if we should warn or raise:
                print(ValueError(f"The path {self.medias_path} is not a folder :/"))

    def run_app(self, native=False, reload=True):
        # NOTE:
        # The nice gui app must be runnable in native mode with:
        # `python -m <self.run_native_module>`
        # and runnable with reload enable with:
        # `python -m <self.run_dev_module>`
        # Use None in the constructor args to see a detailed explaination

        # Do the import here instead of global to have the module
        # loadable even without the [nicegui] extra requirements.
        # (I know...)
        from nicegui import ui, app

        if self.assets_path is not None and self.assets_path.exists():
            app.add_static_files("/assets", self.assets_path)
        if self.medias_path is not None and self.medias_path.exists():
            app.add_media_files("/medias", self.medias_path)

        reload_pattern = "."
        if reload:
            reload_pattern = str(self.reload_root_path)
            print("RELOADING PATTERN:", reload_pattern)
        else:
            print("RELOAD DISABLED.")

        port = None
        if not native:
            port = 8088

        icon_path = (Path(__file__) / ".." / "tgzr_icon.png").resolve()

        # Native mode does not handle icon gracefully, we need this:
        # see https://github.com/zauberzeug/nicegui/discussions/1745#discussioncomment-12326362
        app.native.start_args["icon"] = str(icon_path)

        ui.run(
            host="127.0.0.1",
            port=port,
            dark=self.dark,
            native=native,
            reload=reload,
            uvicorn_reload_dirs=reload_pattern,
            title=f"TGZR - {self.app_name}",
            favicon=icon_path,
        )
