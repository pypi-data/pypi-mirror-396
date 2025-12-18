from typing import Literal

import importlib.metadata

import click
import rich
import rich.table

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session
from ..studio import Studio
from ..project import Project

from .utils import pass_session


@click.group(
    cls=TGZRCliGroup,
    help="Manage Projects in the Studio",
)
def project():
    pass


@project.command()
@click.argument("name")
@click.option("--allow-existing", is_flag=True, default=False)
@click.option(
    "-r",
    "--required-packages",
    multiple=True,
    help='Extra packages to install. Can be set multiple times: -r "my_studio==1.2.3" -r "krita blender kitsu"',
)
@click.option(
    "--default-index",
    help="The URL of the default package index (by default: <https://pypi.org/simple>).",
)
@click.option(
    "-f",
    "--find-links",
    help="path a folder containing packages to install. Usefull in no-internet situations.",
)
@click.option(
    "--allow-prerelease",
    is_flag=True,
    help="Allow installing tgzr using pre-release packages. Default is False.",
)
@pass_session
def create(
    session: Session,
    name,
    allow_existing: bool = False,
    required_packages: list[str] = [],
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
):
    """
    Create a new project with name "NAME" in the current Studio.
    """
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError("Please select a studio first.")

    project = studio.get_project(name)
    if project.exists():
        if not allow_existing:
            raise click.UsageError(
                f'A Project "{name}" already exists in studio "{studio.path}". Use --allow-existing to update it.'
            )

    studio.create_project(
        project_name=name,
        required_packages=required_packages,
        index=default_index,
        find_links=find_links,
        allow_prerelease=allow_prerelease,
    )
    click.echo(f"Project {name!r} created.")


@project.command()
@pass_session
def show(session: Session):
    """Show the project config."""
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError(
            "No Studio selected, use `tgzr --studio <name> ...` to specify one, or `tgzr studio select` to set the default one."
        )
    project: Project | None = session.get_selected_project()
    if project is None:
        raise click.UsageError(
            "No Project selected, use `tgzr --project <name>...` to specify one."
        )
    if not project.exists():
        raise click.UsageError(f'Project "{project.name}" does not exists.')

    click.echo(f'Configuration for Project "{project.name}" ({project.path}):')
    rich.print(project.config)


@project.command()
@pass_session
def packages(session: Session):
    """Show the project packages."""
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError(
            "No Studio selected, use `tgzr --studio <name> ...` to specify one, or `tgzr studio select` to set the default one."
        )
    project: Project | None = session.get_selected_project()
    if project is None:
        raise click.UsageError(
            "No Project selected, use `tgzr --project <name>...` to specify one."
        )
    if not project.exists():
        raise click.UsageError(f'Project "{project.name}" does not exists.')

    packages = project.get_packages()
    table = rich.table.Table(
        "Name",
        "Version",
        "Editable Path",
        title=f'Packages in Project "{project.name}" ({project.path})',
        min_width=80,
    )
    for entry in packages:
        table.add_row(*entry)
    rich.print(table)


@project.command()
@click.option(
    "-f",
    "--group-filter",
    help="Show only this type of plugins (defaults is to show all).",
)
@pass_session
def plugins(session: Session, group_filter: str | None):
    """Show the project plugins."""
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError(
            "No Studio selected, use `tgzr --studio <name> ...` to specify one, or `tgzr studio select` to set the default one."
        )
    project: Project | None = session.get_selected_project()
    if project is None:
        raise click.UsageError(
            "No Project selected, use `tgzr --project <name>...` to specify one."
        )
    if not project.exists():
        raise click.UsageError(f'Project "{project.name}" does not exists.')

    plugins = project.get_plugins(group_filter)
    table = rich.table.Table(
        "Group",
        "Name",
        "Value",
        title=f'Plugins in Project "{project.name}" ({project.path})',
        min_width=80,
    )
    for plugin in plugins:
        table.add_row(plugin.group, plugin.name, plugin.value)
    rich.print(table)


@project.command(
    "run",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.argument(
    "cmd_name",
)
@click.argument("cmd_args", nargs=-1, type=click.UNPROCESSED)
@pass_session
def project_run(session: Session, cmd_name: str, cmd_args: list[str]):
    """
    Run a Project cmd.
    """
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError("Please select a studio first.")
    project: Project | None = session.get_selected_project()
    if project is None:
        raise click.UsageError("Please select a project first.")
    studio.run_cmd(cmd_name, cmd_args, project.name)


@project.command
@click.option(
    "-s",
    "--shell",
    default="auto",
    help='The shell to use, one of ["xonsh", "cmd", "powershell", "auto"] (defaults to "auto").',
)
@pass_session
def shell(
    session: Session,
    shell: Literal["xonsh", "cmd", "powershell", "auto"] = "auto",
):
    """
    Open a shell configured for the studio.
    """
    try:
        studio: Studio | None = session.get_selected_studio()
    except FileNotFoundError:
        raise click.UsageError(
            f'Studio "{session.selected_studio_name}" does not exists.'
        )
    if studio is None:
        raise click.UsageError("Please select a studio or set a default one.")
    project: Project | None = session.get_selected_project()
    if project is None:
        raise click.UsageError("Please select a project first.")
    if not project.exists():
        raise click.UsageError(f"Project {project.name} does not exist.")
    studio.shell(shell_type=shell, project_name=project.name)
