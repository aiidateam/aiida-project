import textwrap
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

import dotenv
from pydantic import BaseSettings
from rich import print

from .project import load_project_class
from .project.base import BaseProject

DEFAULT_PROJECT_STRUCTURE = {
    "setup": [
        "profile",
        "computer",
        "code",
    ],
    "code": [],
}


class ShellType(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"


class ShellGenerator:

    """Class that sets shell environment variables, relevant directories, config files, etc."""

    CD_AIIDA_BASH = """
    cda () {
    source "$aiida_venv_dir/$1/bin/activate"
    cd "$aiida_project_dir/$1"
    }
    """
    CD_AIIDA_FISH = """
    function cda
        source "$aiida_venv_dir/$argv[1]/bin/activate.fish"
        cd "$aiida_project_dir/$argv[1]"
    end
    funcsave -q cda
    """

    ACTIVATE_AIIDA_BASH = """
    export AIIDA_PATH={env_file_path}
    eval "$(_VERDI_COMPLETE={shell_str}_source verdi)"
    """

    ACTIVATE_AIIDA_FISH = """
    set -Ux AIIDA_PATH {env_file_path}
    eval "$(_VERDI_COMPLETE={shell_str}_source verdi)"
    """

    VARIABLE_EXPORT_BASH = "export $(grep -v '^#' {env_file_path} | xargs)"
    VARIABLE_EXPORT_FISH = """
    grep -v '^#' {env_file_path} | sed "s|'||g; s|\\"||g; s|=| |" | while read -l key value
        set -Ux "$key" "$value"
    end
    """

    DEACTIVATE_AIIDA_BASH = "unset AIIDA_PATH"
    DEACTIVATE_AIIDA_FISH = "set -e AIIDA_PATH"

    # def __init__(self, shell_str: str, env_file_path: Optional[Path] = None) -> None:
    def __init__(self, shell_str: str):
        self.shell_str = shell_str
        # self.env_file_path = env_file_path

    def _get_script(self, bash_script: str, fish_script: str) -> str:

        """Helper function to return respective shell script based type. Avoids code duplication.

        Args:
            bash_script (str): Bash codes defined above as class variables.
            fish_script (str): Fish codes defined above as class variables.

        Raises:
            ValueError: If shell type is not one of the supported types.

        Returns:
            str: Respective shell code.
        """

        if self.shell_str in ['bash', 'zsh']:
            return_script = bash_script
        elif self.shell_str == 'fish':
            return_script = fish_script
        else:
            raise ValueError(f'Invalid shell type: {self.shell_str}')
        # ? Remove indentation from multiline string
        return textwrap.dedent(return_script)

    def cd_aiida(self):
        """Define function to `cd` into a given AiiDA project."""
        return self._get_script(self.CD_AIIDA_BASH, self.CD_AIIDA_FISH)

    def activate_aiida(self):
        """Define function to activate a given AiiDA project."""
        return self._get_script(self.ACTIVATE_AIIDA_BASH, self.ACTIVATE_AIIDA_FISH)

    def variable_export(self):
        """Set relevant environment variables."""
        return self._get_script(self.VARIABLE_EXPORT_BASH, self.VARIABLE_EXPORT_FISH)

    def deactivate_aiida(self):
        """Unset AiiDA PATH."""
        return self._get_script(self.DEACTIVATE_AIIDA_BASH, self.DEACTIVATE_AIIDA_FISH)


class ProjectConfig(BaseSettings):
    """Configuration class for configuring `aiida-project`."""

    aiida_venv_dir: Path = Path.home() / Path(".aiida_venvs")
    aiida_project_dir: Path = Path.home() / Path("aiida_projects") # ? Make hidden?
    aiida_default_python_path: Optional[Path] = None
    aiida_project_structure: dict = DEFAULT_PROJECT_STRUCTURE
    aiida_project_shell: str = "bash"

    class Config:
        env_file = Path.home() / Path(".aiida_project.env")
        env_file_encoding = "utf-8"

    def is_not_initialised(self):
        if dotenv.get_key(self.Config.env_file, "aiida_project_shell") is None:
            print("[bold red]Error:[/bold red] The AiiDA project config has not been initialised.")
            print("[bold blue]Info:[/bold blue] Please run `aiida-project init` to get started.")
            return True

    @classmethod
    def from_env_file(cls, env_path: Optional[Path] = None):

        """Populate config instance from env file."""

        if env_path is None:
            env_path = Path.home() / Path(".aiida_project.env")
        # ? Currently works only with default path of Config class...
        config_dict = {k:v for k,v in dotenv.dotenv_values(env_path).items()}
        config_instance = cls.parse_obj(config_dict)
        return config_instance

    # ? Renamed these methods, as they actually write to the env file, and we
    # ? might implement a method that sets the key of the ProjectConfig class?
    def write_key(self, key, value):
        dotenv.set_key(self.Config.env_file, key, value)

    def read_key(self, key):
        return dotenv.get_key(key)


class ProjectDict:
    _projects_path = Path(ProjectConfig().aiida_project_dir, ".aiida_projects")

    def __init__(self):
        if not self._projects_path.exists():
            self._projects_path.joinpath("virtualenv").mkdir(parents=True, exist_ok=True)
            self._projects_path.joinpath("conda").mkdir(parents=True, exist_ok=True)

    @property
    def projects(self) -> Dict[str, BaseProject]:
        projects = {}
        for project_file in self._projects_path.glob("**/*.json"):
            engine = load_project_class(str(project_file.parent.name))
            project = engine.parse_file(project_file)
            projects[project.name] = project
        return projects

    def add_project(self, project: BaseProject) -> None:
        """Add a project to the configuration files."""
        with Path(self._projects_path, project.engine, f"{project.name}.json").open("w") as handle:
            handle.write(project.json())

    def remove_project(self, project: Union[str, BaseProject]) -> None:
        """Remove a project from the configuration files."""
        project = self.projects[project] if isinstance(project, str) else project
        Path(self._projects_path, project.engine, f"{project.name}.json").unlink()
