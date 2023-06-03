import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich import print, prompt
from typing_extensions import Annotated

from ..config import ShellGenerator, ShellType
from ..project import EngineType, load_project_class

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

    # ! When instantiated without arguments, default values aren't picked up for some reason...
    # config = ProjectConfig()
    config = ProjectConfig(
        aiida_venv_dir = Path(Path.home(), ".aiida_venvs"),
        aiida_project_dir = Path(Path.home(), "aiida_projects")
    )

    shell_str = shell.value if shell else None

    if not shell_str:
        shell_str = os.environ.get("SHELL")
        prompt_message = "👋 Hello there! Which shell are you using?"
        prompt_message += f" [blue]({shell_str.split('/')[-1]} detected)" if shell_str else ""
        shell_str = prompt.Prompt.ask(
            prompt=prompt_message, choices=[shell_type.value for shell_type in ShellType]
        )

    shellgenerator = ShellGenerator(shell_str=shell_str)

    config.write_key("aiida_project_shell", shell_str)

    # ? Add this to ShellGenerator?
    if shell_str == 'fish':
        env_file_path = Path.home() / Path(
            os.path.join('.config', 'fish', 'conf.d', 'aiida_project.fish')
            )
        if not env_file_path.exists():
            env_file_path.touch()

    else:
        env_file_path = Path.home() / Path(f".{shell_str}rc")

    if "Created by `aiida-project init`" in env_file_path.read_text():
        print(
            "[bold blue]Report:[/] There is already an `aiida-project` initialization comment in "
            f"{env_file_path}" # ? Removed trailing dot
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
            # ? Pass as function argument, rather than via .format on the returned str?
            handle.write(
                shellgenerator.variable_export().format(
                    env_file_path=config.Config.env_file
                )
            )
            handle.write(shellgenerator.cd_aiida())

    config.write_key(
        "aiida_venv_dir",
        os.environ.get("WORKON_HOME", config.aiida_venv_dir.as_posix()),
    )
    config.write_key("aiida_project_dir", config.aiida_project_dir.as_posix())
    config.write_key(
        "aiida_venv_dir",
        os.environ.get("WORKON_HOME", config.aiida_venv_dir.as_posix()),
    )
    print("✨🚀 AiiDA-project has been initialised! 🚀✨")
    print("Restart your shell to let the changes take effect.")


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
    if config.is_not_initialised():
        return
    else:
        config = config.from_env_file()
    # raise SystemExit("Ciao 👋")

    venv_path = config.aiida_venv_dir / Path(name)
    project_path = config.aiida_project_dir / Path(name)
    shell_str = config.aiida_project_shell
    # ? shell_str should be set as instance variable and is used for the command
    # ? selection. However, it's value is also passed to the string format method.
    # ? Right now, it seems a bit clunky and duplicated...
    shellgenerator = ShellGenerator(shell_str=shell_str)

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

    typer.echo("✨ Creating the project environment and directory.")
    project.create(python_path=python)

    typer.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    project.append_activate_text(
        shellgenerator.activate_aiida().format(
            env_file_path=project_path,
            shell_str=shell_str
        )
    )
    project.append_deactivate_text(shellgenerator.deactivate_aiida())

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