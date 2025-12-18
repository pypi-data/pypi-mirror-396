from pathlib import Path

import click
import rich

from tgzr.cli.utils import TGZRCliGroup

from .utils import pass_session, Session


@click.group(cls=TGZRCliGroup, help="Manage tgzr session configs.")
def session_group():
    pass


@session_group.command()
@pass_session
def show(session):
    rich.print(session.config)


@session_group.command()
@click.option("-o", "--output", help='The file to save. Defaults to "home/.tgzr".')
@click.option("--force", is_flag=True)
@pass_session
def save(session: Session, output: Path | None = None, force: bool = False):
    try:
        session.write_config_file(output, allow_overwrite=force)
    except FileExistsError as err:
        click.echo(f"File {err} already exists! (Use --force to allow overwrite.)")
