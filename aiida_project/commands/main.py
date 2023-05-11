from datetime import datetime
import os
import subprocess
from pathlib import Path
from typing import List, Optional

import typer
from rich import print
from typing_extensions import Annotated

from ..project import EngineType, load_project_class

CDA_FUNCTION = """
cda () {
  source $aiida_venv_dir/$1/bin/activate
  cd $aiida_project_dir/$1
}
"""

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


app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def callback():
    """
    Tool for importing CIF files and converting them into a unique set of `StructureData`.
    """


@app.command()
def init():
    """Initialisation of the `aiida-project` setup."""
    from ..config import ProjectConfig

    config = ProjectConfig()

    shell = os.environ.get("SHELL")
    env_file_path = Path.home() / Path(f".{shell.split('/')[-1]}rc")

    with env_file_path.open("a") as handle:
        handle.write(
            f"\n# Created by `aiida-project init` on {datetime.now().strftime('%d/%m/%y %H:%M')}\n"
        )
        handle.write(f"export $(grep -v '^#' {config.Config.env_file} | xargs)")
        handle.write(CDA_FUNCTION)


@app.command()
def create(
    name: str,
    engine: EngineType = EngineType.virtualenv,
    core_version: str = "latest",
    plugins: Annotated[
        List[str], typer.Option("--plugin", "-p", help="Extra plugins to install.")
    ] = [],
    python: Annotated[
        Optional[Path],
        typer.Option(
            "--python",
            exists=True,
            dir_okay=False,
            file_okay=True,
            help="Path to the Python interpreter to use for the environmnent.",
        ),
    ] = None,
):
    """Create a new AiiDA project named NAME."""
    from ..config import ProjectConfig, ProjectDict

    config = ProjectConfig()

    venv_path = config.aiida_venv_dir / Path(name)
    project_path = config.aiida_project_dir / Path(name)

    project = load_project_class(engine.value)(
        name=name,
        project_path=project_path,
        venv_path=venv_path,
        dir_structure=config.aiida_project_structure,
    )

    typer.echo("✨ Creating the project environment and directory.")
    project.create(python_path=python)

    typer.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    project.append_activate_text(ACTIVATE_AIIDA_SH.format(path=project_path))
    project.append_deactivate_text(DEACTIVATE_AIIDA_SH)

    project_dict = ProjectDict()
    project_dict.add_project(project)
    print("✅ [bold green]Success:[/bold green] Project created.")

    # clone_pypackage(project_path, "aiidateam/aiida_core", branch=core_version)
    if core_version != "latest":
        typer.echo(f"💾 Installing AiiDA core module v{core_version}.")
        project.install(f"aiida-core=={core_version}")
    else:
        typer.echo("💾 Installing the latest release of the AiiDA core module.")
        project.install("aiida-core")

    for plugin in plugins:
        typer.echo(f"💾 Installing {plugin}")
        project.install(plugin)


@app.command()
def destroy(
    name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask for confirmation.")
    ] = False,
):
    """Fully remove both the virtual environment and project directory."""
    from ..config import ProjectDict

    config = ProjectDict()

    try:
        project = config.projects[name]
    except KeyError:
        print(f"[bold red]Error:[/bold red] No project with name {name} found!")
        return

    if not force:
        typer.confirm(
            f"❗️ Are you sure you want to delete the entire {name} project? This cannot be undone!",
            abort=True,
        )

    project.destroy()
    config.remove_project(name)
    print(f"[bold green]Succes:[/bold green] Project with name {name} has been destroyed.")
