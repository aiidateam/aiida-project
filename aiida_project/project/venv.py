import shutil
import subprocess
from pathlib import Path

from aiida_project.project.base import BaseProject


class VenvProject(BaseProject):
    """An AiiDA environment based on `venv`."""

    _engine = "venv"

    def create(self, python_path: Path) -> None:
        super().create(python_path)
        venv_command = [f"{python_path.resolve()}", "-m", "venv", "."]
        self.venv_path.mkdir(
            exist_ok=True,
            parents=True,
        )
        subprocess.run(venv_command, cwd=self.venv_path, capture_output=True)

    def destroy(self):
        """Destroy the project."""
        super().destroy()
        shutil.rmtree(self.venv_path, ignore_errors=True)

    def append_activate_text(self, text):
        with Path(self.venv_path, "bin", "activate").open("a") as handle:
            handle.write(text)

    def append_deactivate_text(self, text):
        with Path(self.venv_path, "bin", "activate").open("r") as handle:
            contents = handle.read()

        # Make sure the content has the right indent - Required to satisfy Python-OCD
        text = "\n".join([" " * 4 + line.lstrip(" ") for line in text.splitlines()])

        with Path(self.venv_path, "bin", "activate").open("w") as handle:
            handle.write(
                contents.replace(
                    "unset VIRTUAL_ENV",
                    f"unset VIRTUAL_ENV\n{text}\n",
                )
            )

    def install(self, package):
        install_command = [Path(self.venv_path, "bin", "pip").as_posix(), "install", package]
        subprocess.run(install_command, capture_output=True)

    def install_local(self, path):
        install_command = []
        install_command.append(Path(self.venv_path, "bin", "pip")).as_posix()
        install_command.extend(["install", "-e", path.as_posix()])
        subprocess.run(install_command, cwd=self.project_path)
