from pathlib import Path

from tgzr.shell.app_sdk.nice_app import ShellNiceApp
from . import run_native, run_dev

from . import pages


app = ShellNiceApp(
    "tgzr_shell_doc",
    run_native_module=run_native,
    run_dev_module=run_dev,
    static_file_path=Path(pages.__file__).parent / "static_files",
)
