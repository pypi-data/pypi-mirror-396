"""
WeWork CLI - Main entry point
"""
import click
from src.cli.commands import (
    make_api,
    make_model,
    make_component,
    make_hook,
    make_migration,
    init_project,
    update_framework,
    version_info,
    set_version,
    create,
)


@click.group()
@click.version_option(version="1.1.2", prog_name="wework")
def cli():
    """
    WeWork Framework CLI
    
    A command-line tool for WeWork Framework to generate components,
    manage projects, and update the framework.
    """
    pass


# Add commands
cli.add_command(create)
cli.add_command(init_project)
cli.add_command(make_api)
cli.add_command(make_model)
cli.add_command(make_component)
cli.add_command(make_hook)
cli.add_command(make_migration)
cli.add_command(update_framework)
cli.add_command(set_version, name="set:version")
cli.add_command(version_info)


if __name__ == "__main__":
    cli()

