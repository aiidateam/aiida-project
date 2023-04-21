import click

from .main import main


@main.command(context_settings={"show_default": True})
@click.argument("name")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Do not ask for confirmation.",
)
def destroy(name, force):
    """Fully remove both the virtual environment and project directory."""
    from ..config import ProjectDict

    config = ProjectDict()

    try:
        project = config.projects[name]
    except KeyError:
        click.echo(f"No project with name {name} found!")
        return

    if click.confirm(
        f"Are you sure you want to delete the entire {name} project? This cannot be undone!"
    ):
        project.destroy()
        config.remove_project(name)
