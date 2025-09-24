import shutil
import subprocess
import sys
from pathlib import Path

from aiida_project.config import ProjectConfig
from aiida_project.project.base import BaseProject


class VenvProject(BaseProject):
    """An AiiDA environment based on `venv`."""

    _engine = "venv"
    # uv should be installed in the same place as aiida-project itself
    _uv_path = (Path(sys.executable).parent / "uv").as_posix()

    shell_activate_mapping: dict = {
        "bash": "activate",
        "zsh": "activate",
        "fish": "activate.fish",
    }
    shell_deactivate_mapping: dict = {
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
        # TODO: uv by default clears the existing folder. Is that okay? Should we guard against it?
        venv_command = [
            self._uv_path,
            "venv",
            "-p",
            f"{python_path.resolve()}",
            str(self.venv_path),
        ]
        subprocess.run(venv_command, capture_output=True)

    def destroy(self):
        """Destroy the project."""
        super().destroy()
        shutil.rmtree(self.venv_path, ignore_errors=True)

    def append_activate_text(self, text):
        activate_file = self.shell_activate_mapping[ProjectConfig().aiida_project_shell]
        with Path(self.venv_path, "bin", activate_file).open("a") as handle:
            handle.write(text)

    def append_deactivate_text(self, text):
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

    def install(self, package):
        python_path = Path(self.venv_path, "bin", "python").as_posix()
        install_command = [self._uv_path, "pip", "install", "-p", python_path, package]
        subprocess.run(install_command, capture_output=True)

    def install_local(self, path):
        python_path = Path(self.venv_path, "bin", "python").as_posix()
        install_command = [
            self._uv_path,
            "pip",
            "install",
            "-p",
            python_path,
            "-e",
            path.as_posix(),
        ]
        subprocess.run(install_command, cwd=self.project_path)
