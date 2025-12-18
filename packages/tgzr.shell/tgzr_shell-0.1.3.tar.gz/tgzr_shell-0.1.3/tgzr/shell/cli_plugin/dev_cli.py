from typing import Literal

from pathlib import Path

import click
import os

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session
from ..workspace import Workspace
from ..studio import Studio

from .utils import pass_session


@click.group(cls=TGZRCliGroup)
def dev():
    """Developer tools"""
    pass


@dev.command()
@click.argument("index_name")
@pass_session
def create_local_index(session: Session, index_name: str):
    """
    Create a package index folder in *home*, and set it as default index on
    the workspace config.
    """
    workspace: Workspace = session.workspace

    pi = session.home / index_name
    pi.mkdir(exist_ok=True)
    workspace.config.default_index = "../" + index_name
    workspace.save_config()


@dev.command()
@click.option(
    "-i",
    "--index_name",
    help="Name of the local index. Default is to get it from Workspaces config.",
)
@click.option(
    "-p", "--project", help="Path of the project to build. Defaults to current path."
)
@click.option(
    "-B",
    "--builder",
    default="hatch",
    help='Builder to use, one of ["hatch", "uv", "build"] (defaults to "hatch").',
)
@pass_session
def build_to_local_index(
    session: Session,
    index_name: str | None,
    project: str | None,
    builder: Literal["hatch", "uv", "build"] = "hatch",
):
    """
    Build the project in the current directory directly in
    the specified local pacakge index (a folder in the *home*)

    Note: `hatch` must be installed, or you must use the --builder option.
    """
    workspace: Workspace = session.workspace

    if workspace is not None:
        index = workspace.resolve_index(index_name)
    else:
        index = workspaces.resolve_index(index_name)

    if index is None:
        raise click.UsageError(
            f"No index_name specified and no default index configured. Use --index-name or `tgzr ws dev create-local-index INDEX_NAME` first."
        )

    if "://" in index:
        raise click.UsageError(
            f'The index "{index}" is not a local path. Select another one with --index-name or create one with `tgzr ws dev create-local-index path/to/index`.'
        )

    local_index = Path(index)
    if not local_index.exists():
        raise click.UsageError(
            f'The folder "{index}" does not exists. Select another one with --index-name or create one with `tgzr ws dev create-local-index path/to/index` first.'
        )

    if builder == "hatch":
        cwd = None
        if project is not None:
            cwd = Path(".").resolve()
            os.chdir(project)
        cmd = f"hatch build {local_index}"
        try:
            os.system(cmd)
        finally:
            if cwd is not None:
                os.chdir(cwd)

    elif builder == "uv":
        src_option = ""
        if project is not None:
            src_option = project
        cmd = f"uv build --out-dir {local_index} {src_option}"
        os.system(cmd)

    elif builder == "build":
        src_option = ""
        if project is not None:
            src_option = project
        cmd = f"python -m build --outdir {local_index} {src_option}"
        os.system(cmd)

    else:
        raise click.UsageError(f"Unsupported builder: {builder!r}")
