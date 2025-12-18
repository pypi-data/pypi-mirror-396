import importlib.metadata
import os
import sys
import subprocess

import click

from tgzr.cli.utils import TGZRCliGroup

from tgzr.cli.add_plugins import BrokenCommand
from ..app_sdk.nice_app import ShellNiceApp
from ..app_sdk.qtpy_app import ShellQtpyApp
from ..app_sdk.exe_app import ShellExeApp


@click.group("app", cls=TGZRCliGroup, help="Run installed applications.")
def app_group():
    pass


def create_nice_run_command(app: ShellNiceApp) -> click.Command:
    @click.command(app.app_name)
    @click.option(
        "-r",
        "--reload",
        is_flag=True,
        help="Reload on code change (will run in browser).",
    )
    @click.option(
        "-d",
        "--detach",
        is_flag=True,
        help="Launch the App in another process to avoid blocking this one.",
    )
    def run_app(reload: bool, detach: bool):
        launcher_module = app.run_native_module.__name__
        if reload:
            if detach:
                raise click.UsageError(
                    "You cant run detached with reload (you wouldnt be able to close the process). Please choose one."
                )
            launcher_module = app.run_dev_module.__name__

        cmd = [sys.executable, "-m", launcher_module]
        click.echo(f"Running command: {' '.join(cmd)}")
        if detach:
            popen = subprocess.Popen(cmd)
            click.echo(f"New Process: {popen}")
        else:
            os.system(" ".join(cmd))

    return run_app


def create_run_command(app: ShellQtpyApp | ShellExeApp) -> click.Command:
    @click.command(app.app_name)
    @click.option(
        "-d",
        "--detach",
        is_flag=True,
        help="Launch the App in another process to avoid blocking this one.",
    )
    def run_app(detach: bool):
        launcher_module = app.run_native_module.__name__
        cmd = [sys.executable, "-m", launcher_module]
        click.echo(f"Running command: {' '.join(cmd)}")
        if detach:
            popen = subprocess.Popen(cmd)
            click.echo(f"New Process: {popen}")
        else:
            os.system(" ".join(cmd))

    return run_app


def install_plugin(group: click.Group):

    group.add_command(app_group)

    entry_point_group = "tgzr.shell.app_plugin"

    all_entry_points = importlib.metadata.entry_points(group=entry_point_group)

    for ep in all_entry_points:
        try:
            app = ep.load()
            if isinstance(app, ShellNiceApp):
                cmd = create_nice_run_command(app)
            else:
                cmd = create_run_command(app)
            app_group.add_command(cmd)
            app.cli_run_cmd_installed(cmd, group)
        except Exception as e:
            app_group.add_command(BrokenCommand(ep, e))
            raise

    return group
