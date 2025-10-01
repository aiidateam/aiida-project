import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated, Optional

import typer
from rich import print, prompt

from ..project import EngineType, load_project_class
from ..shell import ShellType, load_shell

app = typer.Typer(pretty_exceptions_show_locals=False)


@app.callback()
def callback() -> None:
    """
    AiiDA project manager: Isolated Python environments tailored to AiiDA
    with separated project directories, configs, and AiiDA profiles.
    """


@app.command()
def init(shell: Optional[ShellType] = None) -> None:
    """Initialisation of the `aiida-project` setup."""
    from ..config import ProjectConfig

    config = ProjectConfig()

    shell_str = shell.value if shell else ""

    if not shell_str:
        shell_guess = os.environ.get("SHELL", "")
        detected_shell = shell_guess.split("/")[-1] if shell_guess else None
        prompt_message = "👋 Hello there! Which shell are you using?"
        # NOTE: Passing `None` or '' as default bypasses the validation of valid choices,
        # hence the ugly if-else.
        if detected_shell is None:
            shell_str = prompt.Prompt.ask(
                prompt=prompt_message,
                choices=[shell_type.value for shell_type in ShellType],
            )
        else:
            shell_str = prompt.Prompt.ask(
                prompt=prompt_message,
                choices=[shell_type.value for shell_type in ShellType],
                default=detected_shell,
            )

    config.set_key("aiida_project_shell", shell_str)
    shellz = load_shell(shell_str)

    shellz.config_file.touch(exist_ok=True)

    if "Created by `aiida-project init`" in shellz.config_file.read_text():
        print(
            "[bold blue]Report:[/] There is already an `aiida-project` initialization comment in "
            f"{shellz.config_file}"
        )
        add_init_lines = prompt.Confirm.ask("Do you want still want to add the init lines?")
    else:
        add_init_lines = True

    if add_init_lines:
        with shellz.config_file.open("a") as handle:
            handle.write(
                f"\n# Created by `aiida-project init` on "
                f"{datetime.now().strftime('%d/%m/%y %H:%M')}\n"
            )
            handle.write(shellz.init_lines.format(env_file_path=config.model_config["env_file"]))

    config.set_key(
        "aiida_venv_dir",
        os.environ.get("WORKON_HOME", config.aiida_venv_dir.as_posix()),
    )
    config.set_key("aiida_project_dir", config.aiida_project_dir.as_posix())
    print("\n✨🚀 AiiDA-project has been initialised! 🚀✨\n")
    print("[bold blue]Info:[/] For the changes to take effect, run the following command:")
    print(f"\n    source {shellz.config_file.resolve()}\n")
    print("or simply open a new terminal.")


@app.command()
def create(
    name: str,
    engine: EngineType = EngineType.venv,
    core_version: str = "latest",
    plugins: Annotated[
        list[str], typer.Option("--plugin", "-p", help="Extra plugins to install.")
    ] = [],
    python: Annotated[
        Optional[str],
        typer.Option(
            "--python",
            help="Path to the Python interpreter to use for the environment.",
        ),
    ] = None,
) -> None:
    """Create a new AiiDA project named NAME."""
    from ..config import ProjectConfig
    from ..project import ProjectDict

    config = ProjectConfig()
    if config.is_not_initialised():
        sys.exit(os.EX_CONFIG)

    venv_path = config.aiida_venv_dir / Path(name)
    project_path = config.aiida_project_dir / Path(name)

    # Temporarily block `conda` engines until we provide support again
    if engine is EngineType.conda:
        print(
            "[bold red]Error:[/bold red] The `conda` engine is currently disabled until we restore "
            "support."
        )
        sys.exit(os.EX_UNAVAILABLE)

    project = load_project_class(engine.value)(
        name=name,
        project_path=project_path,
        venv_path=venv_path,
        dir_structure=config.aiida_project_structure,
    )
    if python is None:
        python_path = Path(sys.executable)
    else:
        python_path = Path(python)
        if not python_path.exists():
            python_which = shutil.which(python)
            if python_which is None:
                python_which = shutil.which(f"python{python}")
            if python_which is None:
                print("[bold red]Error:[/bold red] Could not resolve path to Python binary.")
                sys.exit(os.EX_USAGE)
            else:
                python_path = Path(python_which)

    print(
        "✨ Creating the project directory and environment using the Python binary:\n"
        f"   [purple]{python_path.resolve()}[/]"
    )
    project.create(python_path=python_path)

    typer.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    shell = load_shell(config.aiida_project_shell)
    project.append_activate_text(shell.activate.format(env_file_path=project_path))
    project.append_deactivate_text(shell.deactivate)

    project_dict = ProjectDict()
    project_dict.add_project(project)
    print("✅ [bold green]Success:[/bold green] Project created.")

    aiida_spec = "aiida-core"
    if core_version != "latest":
        aiida_spec += f"=={core_version}"

    packages = [aiida_spec, *plugins]
    typer.echo(f"💾 Installing packages `{' '.join(packages)}`")
    try:
        project.install(packages)
    except CalledProcessError as e:
        print("[bold red]Error:[/bold red] Package installation failed!")
        typer.echo(e)
        typer.echo(e.stdout.decode())
        typer.echo(e.stderr.decode())
        sys.exit(1)


@app.command()
def destroy(
    name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Do not ask for confirmation.")
    ] = False,
) -> None:
    """Fully remove both the virtual environment and project directory."""
    from ..config import ProjectConfig
    from ..project import ProjectDict

    if ProjectConfig().is_not_initialised():
        sys.exit(os.EX_CONFIG)

    project_dict = ProjectDict()

    try:
        project = project_dict.projects[name]
    except KeyError:
        print(f"[bold red]Error:[/bold red] No project with name {name} found!")
        sys.exit(os.EX_USAGE)

    if not force:
        typer.confirm(
            f"❗️ Are you sure you want to delete the entire {name} project? This cannot be undone!",
            abort=True,
        )

    project.destroy()
    project_dict.remove_project(name)
    print(f"[bold green]Succes:[/bold green] Project with name {name} has been destroyed.")
