import click

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session, set_default_session

from .session_cli import session_group
from .workspace_cli import workspace
from .studio_cli import studio, studio_help
from .project_cli import project
from . import app_cli
from .help_cli import env_help
from .dev_cli import dev
from .utils import pass_session


def session_cwd(ctx, param, cwd):
    if cwd is None:
        cwd = "."
    session = Session(cwd)
    set_default_session(session)  # usefull for plugins

    ctx.obj = session
    click.echo(f"TGZR Session: home={session.home}")


@pass_session
def session_verbose(session: Session, ctx, param, value):
    if value:
        session.set_verbose()


@pass_session
def session_quiet(session: Session, ctx, param, value):
    if value:
        session.set_quiet()


@pass_session
def select_studio(session: Session, ctx, param, value):
    session.select_studio(value)
    if value is not None:
        click.echo(f"Using studio {value}")


@pass_session
def select_project(session: Session, ctx, param, value):
    session.select_project(value)
    if value is not None:
        click.echo(f"Using project {value}")


def install_options(group: click.Group):
    # (see https://click.palletsprojects.com/en/stable/advanced/#id2)

    click.option(
        "-H",
        "--home",
        default=None,
        help="Folder to search for TGZR installation (default is current directory).",
        is_eager=True,
        callback=session_cwd,
        metavar="HOME",
    )(group)
    click.option(
        "-v",
        "--verbose",
        is_flag=True,
        # flag_value="",
        help="Chatty mode.",
        callback=session_verbose,
    )(group)
    click.option(
        "--quiet",
        is_flag=True,
        # flag_value="",
        help="Quiet mode (cancels --verbose).",
        callback=session_quiet,
    )(group)
    click.option(
        "-S",
        "--studio",
        default=None,
        help="select a studio (default is defined in the workspace).",
        callback=select_studio,
        metavar="STUDIO-NAME",
    )(group)
    click.option(
        "-P",
        "--project",
        default=None,
        help="select a project (default is defined in the studio).",
        callback=select_project,
        metavar="PROJECT-NAME",
    )(group)


def install_cli(group: TGZRCliGroup):
    cmd, kwargs, setter = group.get_default_command()
    if not setter or setter.startswith("tgzr.cli"):
        # Only uninstall if the default cmd was set by tgzr.cli
        # i.e: only override if the default cmd is "install"
        # print("tgzr.shell Uninstalling default cmd from", setter)
        group.set_default_command(None)

    install_options(group)

    group.add_command(session_group)
    group.add_command(workspace)
    group.add_command(studio)
    group.add_command(project)
    group.add_command(dev)

    help = group.find_group("help")
    if help is None:
        raise Exception("Could not find the cli help group :/")

    help.add_command(env_help)
    help.add_command(studio_help)

    app_cli.install_plugin(group)
