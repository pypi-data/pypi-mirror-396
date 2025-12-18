# tgzr.shell
tgzr workstation runtime

# Create a Shell Application plugin:

There are 3 types or shell app you can provide:
- [NiceGUI](https://nicegui.io/) App:
    - Insall `tgzr.shell[nicegui]`
    - Use `tgzr.shell.app_sdk.nice_app.ShellNiceApp`
- [qtpy](https://pypi.org/project/QtPy/) App:
    - Insall `tgzr.shell[qt]` will install `qtpy` and `PySide6`
    -   Note: If you prefer using PyQt, you can install `tgzr.shell`+`qtpy`+`PyQt6`
    - Use `tgzr.shell.app_sdk.qtpy.ShellQtpyApp`
- Executable file App:
    - Simply install `tgzr.shell`
    - Use `tgzr.shell.app_sdk.exe_app.ShellExeApp`

## Nice app example
To implement a NiceGUI app plugin, you need to:
- install `tgzr.shell[nicegui]`
- create an instance of a `tgzr.shell.app_sdk.ShellApp`
- add an entry point in the group "tgzr.shell.app_plugin" pointing to that app


**Here is a minimalist workging example:**
> 
> **your_package/app.py**:
> ```python
> from . import run_native, run_dev, pages
> from tgzr.shell.app_skd.nice_app import ShellNiceApp
> 
> app = ShellNiceApp(
>     "app_name",
>     run_native_module=run_native,
>     run_dev_module=run_dev,
>     static_file_path=Path(pages.__file__).parent / "static_files",
> )
> ``` 
>
> **your_package/pages.py**:
> ```python
> from nicegui import ui
> 
> 
> @ui.page("/", title="My App")
> async def main():
>     ui.label("Hello world! 😛")
> ```
> 
> **your_package/run_native.py**:
> ```python
> if __name__ == "__main__":
>    from .app import app
>
>    app.run_app(native=True, reload=False)
> ``` 
>
> **your_package/run_dev.py**:
> ```python
> if __name__ in {"__main__", "__mp_main__"}:
>     from .app import app
>    app.run_app(native=False, reload=True)
> ``` 
>
> **pyproject.toml**:
> ```
> [project.entry-points."tgzr.shell.app_plugin"]
> my_shell_app = "your_package:app"
> ```


