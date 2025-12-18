import click
import rich
import rich.table


from .utils import pass_session, Session


@click.command("env")
@pass_session
def env_help(session: Session):
    config_env_vars = session.get_config_env_vars()

    for name, env_vars in config_env_vars:
        table = rich.table.Table("Name", "Description", title=name)

        for name, description in env_vars:
            table.add_row(name, description or "")

        rich.print("\n", table)
