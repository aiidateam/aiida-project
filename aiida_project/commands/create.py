import subprocess
from pathlib import Path

import click

from ..commands.main import main
from ..project import get_project

ACTIVATE_AIIDA_SH = """
export AIIDA_PATH={path}

if test -x "$(command -v verdi)"
then
    eval "$(_VERDI_COMPLETE=source-bash verdi)"
fi
"""

DEACTIVATE_AIIDA_SH = "unset AIIDA_PATH"


def clone_pypackage(project_path, repo, branch=None):
    clone_command = ["git", "clone", "--single-branch"]
    if branch:
        clone_command.extend(["-b", branch])
    clone_command.append(f"https://github.com/{repo}")
    subprocess.call(clone_command, cwd=project_path.strpath)


@main.command(context_settings={"show_default": True})
@click.argument("name")
@click.option(
    "--engine",
    default="virtualenv",
    type=click.Choice(["virtualenv", "wrapper", "conda"]),
    help="virtualenv engine",
)
@click.option(
    "--core-version",
    help="If specified, immediately installs the corresponding version of `aiida-core`.",
)
@click.option(
    "--plugins",
    multiple=True,
    help="plugin specifier <github_user>/<repo>:<branch>",
)
@click.option("--python", type=click.Path(file_okay=True, exists=True, dir_okay=False))
def create(name, engine, core_version, plugins, python):
    """Create a new AiiDA project named NAME."""
    from ..config import ProjectConfig, ProjectDict

    config = ProjectConfig()

    venv_path = config.aiida_venv_dir / Path(name)
    project_path = config.aiida_project_dir / Path(name)

    project = get_project(engine=engine, name=name, project_path=project_path, venv_path=venv_path)

    click.echo("✨ Creating the project environment and directory.")
    project.create(python_path=python)

    click.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    project.append_activate_text(ACTIVATE_AIIDA_SH.format(path=project_path))
    project.append_deactivate_text(DEACTIVATE_AIIDA_SH)

    project_dict = ProjectDict()
    project_dict.add_project(project)
    click.echo("✅ Success! Project created.")

    # clone_pypackage(project_path, "aiidateam/aiida_core", branch=core_version)
    if core_version is not None:
        click.echo(f"💾 Installing AiiDA core module v{core_version}.")
        project.install(f"aiida-core=={core_version}")
    else:
        click.echo("💾 Installing the latest release of the AiiDA core module.")
        project.install("aiida-core")

    for plugin in plugins:
        click.echo(f"💾 Installing {plugin}")
        project.install(plugin)
