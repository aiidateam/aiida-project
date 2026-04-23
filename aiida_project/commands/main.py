import os
import shutil
import sys
from pathlib import Path
from subprocess import CalledProcessError
from typing import Annotated

import typer
from rich import print, prompt

from ..project import EngineType, load_project_class
from ..shell import ShellType, load_shell

app = typer.Typer(pretty_exceptions_show_locals=False)

_NOT_INITIALISED_MSG = (
    "[bold red]Error:[/bold red] The AiiDA project config has not been initialised.\n"
    "[bold blue]Info:[/bold blue] Please run `aiida-project init` to get started."
)


@app.callback()
def callback(ctx: typer.Context) -> None:
    """
    AiiDA project manager: Isolated Python environments tailored to AiiDA
    with separated project directories, configs, and AiiDA profiles.
    """
    if ctx.invoked_subcommand == "init":
        return

    from ..config import ProjectConfig

    config = ProjectConfig()
    if not config.is_initialised():
        return

    shell = load_shell(config.aiida_project_shell)
    if shell.is_outdated:
        print(
            "⚠️  [bold yellow]Warning:[/] Shell configuration is outdated. "
            "Run [bold]aiida-project init[/bold] to update."
        )


@app.command()
def init(shell: ShellType | None = None) -> None:
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

    is_reinit = shellz.write_config(str(config.model_config["env_file"]))

    rc_file = ShellType(shell_str).rc_file

    if rc_file is not None:
        shellz.ensure_source_line(rc_file)

    config.set_key(
        "aiida_venv_dir",
        os.environ.get("WORKON_HOME", config.aiida_venv_dir.as_posix()),
    )
    config.set_key("aiida_project_dir", config.aiida_project_dir.as_posix())

    if is_reinit:
        print("\n🔄 AiiDA-project shell configuration has been updated.\n")
    else:
        print("\n✨🚀 AiiDA-project has been initialised! 🚀✨\n")

    print("[bold blue]Info:[/] For the changes to take effect, run the following command:")
    print(f"\n    source {shellz.config_file.resolve()}\n")
    print("or simply open a new terminal.")


@app.command()
def create(  # noqa: PLR0915
    name: str,
    engine: EngineType = EngineType.venv,
    core_version: str = "latest",
    plugins: Annotated[
        list[str], typer.Option("--plugin", "-p", help="Extra plugins to install.")
    ] = [],
    python: Annotated[
        str | None,
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
    if not config.is_initialised():
        print(_NOT_INITIALISED_MSG)
        sys.exit(os.EX_CONFIG)

    # Guard against user putting an empty string (allowed by typer!)
    if not name:
        print("[bold red]Error:[/bold red] Project name cannot be an empty string.'")
        sys.exit(os.EX_USAGE)

    project_dict = ProjectDict()
    if name in project_dict.projects:
        print(f"[bold red]Error:[/bold red] Project named '{name}' already exists!")
        sys.exit(os.EX_USAGE)

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
            python_which = shutil.which(python) or shutil.which(f"python{python}")
            if python_which is None:
                print("[bold red]Error:[/bold red] Could not resolve path to Python binary.")
                sys.exit(os.EX_USAGE)
            else:
                python_path = Path(python_which)

    print(
        "✨ Creating the project directory and environment using the Python binary:\n"
        f"   [purple]{python_path.resolve()}[/]"
    )

    try:
        project.create(python_path=python_path)
    except CalledProcessError as e:
        print("[bold red]Error:[/bold red] Python environment creation failed!")
        typer.echo(e)
        typer.echo(e.stdout.decode())
        typer.echo(e.stderr.decode())
        sys.exit(1)

    typer.echo("🔧 Adding the AiiDA environment variables to the activate script.")
    shell = load_shell(config.aiida_project_shell)
    project.append_activate_text(shell.activate.format(env_file_path=project_path))
    project.append_deactivate_text(shell.deactivate)

    project_dict.add_project(project)
    print("✅ [bold green]Success:[/bold green] Project created.")

    aiida_spec = "aiida-core"
    if core_version != "latest":
        aiida_spec += f"=={core_version}"

    packages = [aiida_spec, *plugins]
    typer.echo(f"💾 Installing `{' '.join(packages)}`")
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

    if not ProjectConfig().is_initialised():
        print(_NOT_INITIALISED_MSG)
        sys.exit(os.EX_CONFIG)

    project_dict = ProjectDict()

    try:
        project = project_dict.projects[name]
    except KeyError:
        print(f"[bold red]Error:[/bold red] No project named '{name}' found!")
        sys.exit(os.EX_USAGE)

    if not force:
        typer.confirm(
            f"❗️ Are you sure you want to delete the entire '{name}' project? "
            f"This cannot be undone!",
            abort=True,
        )

    project.destroy()
    project_dict.remove_project(name)
    print(f"[bold green]Success:[/bold green] Project '{name}' has been destroyed.")


@app.command(name="list")
def list_projects() -> None:
    """List all existing projects."""
    from rich.table import Table

    from ..config import ProjectConfig
    from ..project import ProjectDict

    if not ProjectConfig().is_initialised():
        sys.exit(os.EX_CONFIG)

    projects = ProjectDict().projects

    if not projects:
        print(
            "[bold blue]Info:[/] No projects found. "
            "Create one with [bold]aiida-project create <name>[/bold]."
        )
        return

    table = Table()
    table.add_column("Name", style="bold green")
    table.add_column("Engine", style="blue")
    table.add_column("Project Path", style="dim")
    table.add_column("Environment Path", style="dim")

    for name, project in sorted(projects.items()):
        table.add_row(
            name,
            project.engine,
            str(project.project_path),
            str(project.venv_path),
        )

    print()
    print(table)
