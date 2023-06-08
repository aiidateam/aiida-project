import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich import print, prompt
from typing_extensions import Annotated

from ..config import ShellType
from ..project import EngineType, load_project_class

CDA_FUNCTION = """
cda () {
  source $aiida_venv_dir/$1/bin/activate
  cd $aiida_project_dir/$1
}
"""

ACTIVATE_AIIDA_SH = """
export AIIDA_PATH={path}
eval "$(_VERDI_COMPLETE={shell}_source verdi)"
"""

DEACTIVATE_AIIDA_SH = "unset AIIDA_PATH"


app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def callback():
    """
    Tool for importing CIF files and converting them into a unique set of `StructureData`.
    """


@app.command()
def init(shell: Optional[ShellType] = None):
    """Initialisation of the `aiida-project` setup."""
    from ..config import ProjectConfig

    config = ProjectConfig()

    shell_str = shell.value if shell else None

    if not shell_str:
        shell_str = os.environ.get("SHELL")
        prompt_message = "👋 Hello there! Which shell are you using?"
        prompt_message += f" [blue]({shell_str.split('/')[-1]} detected)" if shell_str else ""
        shell_str = prompt.Prompt.ask(
            prompt=prompt_message, choices=[shell_type.value for shell_type in ShellType]
        )

    if shell_str == "fish":
        print(
            "[bold red]Error:[/] `fish` is not yet supported. "
            "If this is Julian: you better get to it 😜"  # Nhehehe
        )
        return

    config.set_key("aiida_project_shell", shell_str)

    env_file_path = Path.home() / Path(f".{shell_str}rc")

    if "Created by `aiida-project init`" in env_file_path.read_text():
        print(
            "[bold blue]Report:[/] There is already an `aiida-project` initialization comment in "
            f"{env_file_path}."
        )
        add_init_lines = prompt.Confirm.ask("Do you want still want to add the init lines?")
    else:
        add_init_lines = True

    if add_init_lines:
        with env_file_path.open("a") as handle:
            handle.write(
                f"\n# Created by `aiida-project init` on "
                f"{datetime.now().strftime('%d/%m/%y %H:%M')}\n"
            )
            handle.write(f"export $(grep -v '^#' {config.Config.env_file} | xargs)")
            handle.write(CDA_FUNCTION)

    config.set_key(
        "aiida_venv_dir",
        os.environ.get("WORKON_HOME", config.aiida_venv_dir.as_posix()),
    )
    config.set_key("aiida_project_dir", config.aiida_project_dir.as_posix())
    print("✨🚀 AiiDA-project has been initialised! 🚀✨")


@app.command()
def create(
    name: str,
    engine: EngineType = EngineType.venv,
    core_version: str = "latest",
    plugins: Annotated[
        List[str], typer.Option("--plugin", "-p", help="Extra plugins to install.")
    ] = [],
    python: Annotated[
        Optional[str],
        typer.Option(
            "--python",
            help="Path to the Python interpreter to use for the environment.",
        ),
    ] = None,
):
    """Create a new AiiDA project named NAME."""
    from ..config import ProjectConfig, ProjectDict

    config = ProjectConfig()
    if config.is_not_initialised():
        return

    venv_path = config.aiida_venv_dir / Path(name)
    project_path = config.aiida_project_dir / Path(name)

    # Temporarily block `conda` engines until we provide support again
    if engine is EngineType.conda:
        print(
            "[bold red]Error:[/bold red] The `conda` engine is currently disabled until we restore "
            "support."
        )
        return

    project = load_project_class(engine.value)(
        name=name,
        project_path=project_path,
        venv_path=venv_path,
        dir_structure=config.aiida_project_structure,
    )
    if python is not None:
        python_path = Path(python)

        if not python_path.exists():
            python_which = shutil.which(python)
            if python_which is None:
                python_which = shutil.which(f"python{python}")
            if python_which is None:
                print("[bold red]Error:[/bold red] Could not resolve path to Python binary.")
                return
            else:
                python_path = Path(python_which)

    typer.echo("✨ Creating the project environment and directory.")
    project.create(python_path=python_path)

    typer.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    project.append_activate_text(
        ACTIVATE_AIIDA_SH.format(path=project_path, shell=config.aiida_project_shell)
    )
    project.append_deactivate_text(DEACTIVATE_AIIDA_SH)

    project_dict = ProjectDict()
    project_dict.add_project(project)
    print("✅ [bold green]Success:[/bold green] Project created.")

    if core_version != "latest":
        typer.echo(f"💾 Installing AiiDA core module v{core_version}.")
        project.install(f"aiida-core=={core_version}")
    else:
        typer.echo("💾 Installing the latest release of the AiiDA core module.")
        project.install("aiida-core")

    for plugin in plugins:
        if "github.com" in plugin:
            clone_path = project.project_path / Path("git") / Path(plugin.split("/")[-1]).stem
            typer.echo(f"⬇️  Cloning repo `{plugin}` from GitHub to `{clone_path.resolve()}`.")
            project.clone_repo(plugin, clone_path)
            typer.echo(f"💾 Installing local repo `{clone_path}` as editable install.")
        else:
            typer.echo(f"💾 Installing `{plugin}` from PyPI.")
            project.install(plugin)


@app.command()
def destroy(
    name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask for confirmation.")
    ] = False,
):
    """Fully remove both the virtual environment and project directory."""
    from ..config import ProjectConfig, ProjectDict

    if ProjectConfig().is_not_initialised():
        return

    project_dict = ProjectDict()

    try:
        project = project_dict.projects[name]
    except KeyError:
        print(f"[bold red]Error:[/bold red] No project with name {name} found!")
        return

    if not force:
        typer.confirm(
            f"❗️ Are you sure you want to delete the entire {name} project? This cannot be undone!",
            abort=True,
        )

    project.destroy()
    project_dict.remove_project(name)
    print(f"[bold green]Succes:[/bold green] Project with name {name} has been destroyed.")
