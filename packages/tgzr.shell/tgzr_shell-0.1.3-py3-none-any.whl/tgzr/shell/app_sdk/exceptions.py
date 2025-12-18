class MissingRunDevModule(ValueError):
    def __init__(self, app):
        super().__init__(
            f"""
The app {app.shell_app_id()} does not define the `RUN_DEV_MODULE` attribute.

Your app must be runnable with this command:
    `python -m your_app_package.your_show_dev_module`
Or if you're using uv:
    `uv run python -m your_app_package.your_show_dev_module`

You must implement "your_show_**dev**_module" whith this content:

```python

from your_app_package import YourAppClass

if __name__ in {"__main__", "__mp_main__"}:
    YourAppClass().run_app(native=False, reload=True)
```

"""
        )


class MissingRunNativeModule(ValueError):
    def __init__(self, app):
        super().__init__(
            f"""
The app {app.shell_app_id()} does not define the `RUN_NATIVE_MODULE` attribute.

Your app must be runnable with this command:
    `python -m your_app_package.your_show_nativ_module`
Or if you're using uv:
    `uv run python -m your_app_package.your_show_native_module`

You must implement "your_show_**native**_module" whith this content:

```python

from your_app_package import YourAppClass

if __name__ == "__main__":
    YourAppClass().run_app(native=True, reload=False)
```
"""
        )
