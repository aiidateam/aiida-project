import shutil
import subprocess
import sys
from pathlib import Path
from typing import ClassVar

from aiida_project.config import ProjectConfig
from aiida_project.project.base import BaseProject

__all__ = ["VenvProject"]

# uv should be installed in the same place as aiida-project itself
# NOTE: We convert Path to str here for type-checking purposes. :-/
UV_EXE = (Path(sys.executable).parent / "uv").as_posix()
if not Path(UV_EXE).is_file():
    if (which_uv := shutil.which("uv")) is None:
        sys.exit("ERROR: Could not find uv executable. Maybe try re-installing aiida-project?")
    else:
        UV_EXE = which_uv


class VenvProject(BaseProject):
    """An AiiDA environment based on `venv`."""

    _engine = "venv"

    shell_activate_mapping: ClassVar[dict[str, str]] = {
        "bash": "activate",
        "zsh": "activate",
        "fish": "activate.fish",
    }
    shell_deactivate_mapping: ClassVar[dict[str, str]] = {
        "bash": "deactivate () {",
        "zsh": "deactivate () {",
        "fish": 'function deactivate -d "Exit virtual environment"',
    }

    def create(self, python_path: Path) -> None:
        super().create(python_path)
        self.venv_path.mkdir(
            exist_ok=True,
            parents=True,
        )
        venv_command = [
            UV_EXE,
            "venv",
            "--no-project",
            "--allow-existing",
            "--seed",
            "-p",
            f"{python_path.resolve()}",
            str(self.venv_path),
        ]
        subprocess.run(venv_command, check=True, capture_output=True)

    def destroy(self) -> None:
        """Destroy the project."""
        super().destroy()
        shutil.rmtree(self.venv_path, ignore_errors=True)

    def append_activate_text(self, text: str) -> None:
        activate_file = self.shell_activate_mapping[ProjectConfig().aiida_project_shell]
        with Path(self.venv_path, "bin", activate_file).open("a") as handle:
            handle.write(text)

    def append_deactivate_text(self, text: str) -> None:
        activate_file = self.shell_activate_mapping[ProjectConfig().aiida_project_shell]
        with Path(self.venv_path, "bin", activate_file).open("r") as handle:
            contents = handle.read()

        # Make sure the content has the right indent - Required to satisfy Python-OCD
        text = "\n".join([" " * 4 + line.lstrip(" ") for line in text.splitlines()])
        replace_line = self.shell_deactivate_mapping[ProjectConfig().aiida_project_shell]

        with Path(self.venv_path, "bin", activate_file).open("w") as handle:
            handle.write(
                contents.replace(
                    replace_line,
                    replace_line + f"\n{text}\n",
                )
            )

    def install(self, packages: list[str]) -> None:
        python_path = Path(self.venv_path, "bin", "python").as_posix()
        install_command = [UV_EXE, "pip", "install", "-p", python_path, *packages]
        subprocess.run(install_command, capture_output=True, check=True)
