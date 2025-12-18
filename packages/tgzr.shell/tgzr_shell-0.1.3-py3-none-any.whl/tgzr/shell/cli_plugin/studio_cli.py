from typing import Literal


import click
import rich
import rich.table

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session
from ..workspace import Workspace
from ..studio import Studio

from .utils import pass_session


@click.command("studio")
def studio_help():
    rich.print("Sorry, this help is not written yet :p")


@click.group(cls=TGZRCliGroup, help="Manage tgzr studios")
def studio():
    pass


@studio.command()
@click.argument("name")
@click.option("--allow-existing", is_flag=True, default=False)
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
@click.option(
    "-N",
    "--not-default",
    is_flag=True,
    default=False,
    help="Do not make this created studio the default one.",
)
@pass_session
def create(
    session: Session,
    name,
    allow_existing: bool = False,
    default_index: str | None = None,
    find_links: str | None = None,
    allow_prerelease: bool = False,
    not_default: bool = True,
):
    """
    Create a new Studio with name "NAME".
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No workspace found at {session.home}.")
    studio = workspace.get_studio(name, ensure_exists=False)
    if studio.exists():
        if not allow_existing:
            raise click.UsageError(
                f'A Studio "{name}" already exists in workspace "{workspace.path}". Use --allow-existing to update it.'
            )

    studio.create(
        index=default_index,
        find_links=find_links,
        allow_prerelease=allow_prerelease,
    )
    click.echo(f"Studio {name!r} created.")

    # Ensure the studio config is written so the session's home can
    # be discovered:
    session.save_config()

    if not_default:
        return

    workspace.set_default_studio(name)
    click.echo(f'Studio "{name}" set as default studio.')


@studio.command()
@pass_session
def ls(session: Session):
    """
    List the installed Studio.
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No workspace found at {session.home}.")
    default_studio_name = workspace.default_studio_name()
    for studio in workspace.get_studios():
        default_indic = ""
        if studio.name == default_studio_name:
            default_indic = "*"
        click.echo(f"  {studio.name}{default_indic} ({studio.path})")


@studio.command()
@pass_session
def show(session: Session):
    """Show the studio config."""
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

    click.echo(f'Configuration for Studio "{studio.name}" ({studio.path}):')
    rich.print(studio.config)


@studio.command()
@pass_session
def select(session: Session):
    """
    Set the default studio (without -S or --studio, resets default to None).
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No workspace found at {session.home}.")

    default_studio_name = workspace.default_studio_name()
    studio: Studio | None = session.get_selected_studio()
    if studio is None:
        workspace.set_default_studio(None)
    else:
        if studio.name == default_studio_name:
            click.echo(f"The default Studio is already {default_studio_name}.")
        else:
            workspace.set_default_studio(studio.name)


@studio.command()
@pass_session
def switch(session: Session):
    """
    Change the default studio.
    """
    workspace: Workspace | None = session.workspace
    if workspace is None:
        raise click.UsageError(f"No workspace found at {session.home}.")

    studio_names = workspace.studio_names()
    if not studio_names:
        click.echo('No Studio installed yet. Use "tgzr studio create" to add one.')
        return

    click.echo("0 <None>")
    for i, name in enumerate(studio_names, start=1):
        click.echo(f"{i} {name}")
    value = click.prompt("Enter Studio")
    if value.strip() == "0":
        workspace.set_default_studio(None)
        return

    name = None
    try:
        index = int(value)
    except ValueError:
        if value in studio_names:
            name = value
    else:
        try:
            name = studio_names[index - 1]
        except:
            pass

    if name is None:
        click.echo("Nope ¯\\_(ツ)_/¯")
    else:
        workspace.set_default_studio(name)


@studio.command()
@pass_session
@click.option(
    "--default-index",
    help=(
        "Set the url of the default package index, like "
        '"https://pypi.org/simple", "/path/to/folder" or "./path/relative/to/workspace". '
        'Use "" to unset.'
    ),
)
def set(session: Session, **kwargs):
    """
    Set some config field in the Studio config.
    """
    studio: Studio | None = session.get_selected_studio()
    if studio is None:
        raise click.UsageError("Please select a studio or set a default one.")

    not_None_options = [n for n, v in kwargs.items() if v is not None]
    if not not_None_options:
        raise click.UsageError("Please specify at least one option.")

    # print(kwargs)

    if (default_index := kwargs["default_index"]) is not None:
        if not default_index:
            default_index = None
        studio.config.default_index = default_index

    path = studio.save_config()
    click.echo(f"Config saved: {path}")


@studio.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument(
    "cmd_name",
)
@click.argument("cmd_args", nargs=-1, type=click.UNPROCESSED)
@pass_session
def run(session: Session, cmd_name: str, cmd_args: list[str]):
    """
    Run a studio cmd.
    """
    studio: Studio | None = session.get_selected_studio()
    if studio is None:
        raise click.UsageError("Please select a studio or set a default one.")

    studio.run_cmd(cmd_name, cmd_args, project_name=None)


@studio.command
@click.option(
    "-s",
    "--shell",
    default="auto",
    help='The shell to use, one of ["xonsh", "bash", "cmd", "powershell", "auto"] (defaults to "auto").',
)
@pass_session
def shell(
    session: Session,
    shell: Literal["xonsh", "cmd", "powershell", "auto"] = "auto",
):
    """
    Open a shell configured for the studio.
    """
    studio: Studio | None = session.get_selected_studio()
    if studio is None:
        raise click.UsageError("Please select a studio or set a default one.")
    studio.shell(shell_type=shell, project_name=None)


@studio.command("plugins-here")
@click.option(
    "--format",
    default="table",
    help='Output format, one of ["table", "json"] (defaults to "table").',
)
@click.option(
    "-f",
    "--group-filter",
    help="Show only this type of plugins (defaults is to show all).",
)
@pass_session
def plugins_here(session: Session, format: str, group_filter: str | None):
    """
    Prints the list of plugins loaded in the current interpretor.
    If group-filter is given, the list is sorted by group.
    """
    import importlib.metadata
    import json

    entry_points = importlib.metadata.entry_points()
    if group_filter is not None:
        entry_points = [ep for ep in entry_points if group_filter in ep.group]
        entry_points.sort(key=lambda e: e.group)
    else:
        entry_points = list(entry_points)
        entry_points.sort(key=lambda e: e.module)

    if format == "table":
        table = rich.table.Table("Group", "Name", "Value")
        for ep in entry_points:
            table.add_row(ep.group, ep.name, ep.value)
        rich.print(table)
    elif format == "json":
        data = []
        for ep in entry_points:
            data.append(dict(group=ep.group, name=ep.name, value=ep.value))
        print(">>> JSON:")
        print(json.dumps(data, indent=None))
    else:
        raise click.UsageError(f"Unknown --format option {format!r}.")


@studio.command()
@click.option(
    "-f",
    "--group-filter",
    help="Show only this type of plugins (defaults is to show all).",
)
@pass_session
def plugins(session: Session, group_filter: str | None):
    """Show the plugins installed in the studio venv."""
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

    plugins = studio.get_plugins(None, group_filter)
    table = rich.table.Table(
        "Group",
        "Name",
        "Value",
        title=f'Plugins in Studio "{studio.name}" ({studio.path})',
        min_width=80,
    )
    for plugin in plugins:
        table.add_row(plugin.group, plugin.name, plugin.value)
    rich.print(table)
