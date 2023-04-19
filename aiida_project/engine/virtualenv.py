import subprocess

from aiida_project.engine.base import BaseEngine


class VirtualenvEngine(BaseEngine):
    def create(self, name, python=None):
        self._venv_name = f"venv-{name}"
        venv_command = ["virtualenv", self.venv_name]
        if python:
            venv_command.append(f"--python={python}")
        subprocess.check_call(venv_command, cwd=self.project_path.strpath)
        self._venv_path = self.project_path.join(self.venv_name)

    def install(self, path):
        install_command = []
        install_command.append(self.venv_path.join("bin", "pip").strpath)
        install_command.extend(["install", "-e", path.strpath])
        subprocess.check_call(install_command, cwd=self.project_path.strpath)

    def add_activate_script(self, path):
        activate_script = self.venv_path.join("bin", "activate")
        activate_script.write(f"source {path.strpath}", mode="a")

    def add_deactivate_script(self, path):
        deactivate_script = self.venv_path.join("bin", "deactivate")
        deactivate_script.write(f"source {path.strpath}", mode="a")
