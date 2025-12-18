from typing import Literal

import click
import rich

from tgzr.cli.utils import TGZRCliGroup

from ..workspace import Workspace
from .utils import pass_session, Session


@click.group(
    cls=TGZRCliGroup,  # to allow command short names
    help="Manage the workspace configuration",
)
def workspace():
    pass


@workspace.command("show")
@pass_session
def workspace_show(session: Session):
    """
    Show the Workspace configuration.
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No Workspace found in {session.home}")
    rich.print(workspace.config)


@workspace.command("set")
@pass_session
@click.option(
    "--default-index",
    help=(
        "Set the url of the default package index, like "
        '"https://pypi.org/simple", "/path/to/folder" or "./path/relative/to/workspace". '
        'Use "" to unset.'
    ),
)
def workspace_set(session: Session, **kwargs):
    """
    Set some config field in the Workspace config.
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No Workspace found in {session.home}")

    not_None_options = [n for n, v in kwargs.items() if v is not None]
    if not not_None_options:
        raise click.UsageError("Please specify at least one option.")

    # print(kwargs)

    if (default_index := kwargs["default_index"]) is not None:
        if not default_index:
            default_index = None
        workspace.config.default_index = default_index

    path = workspace.save_config()
    click.echo(f"Config saved: {path}")
